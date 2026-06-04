from django.conf import settings
from django.db import models
from django.db.models import F, GeneratedField

from inventory.choices import (
    Prioridade,
    StatusInventario,
    StatusOperacional,
    StatusOrdemServico,
    StatusRequisicao,
    TipoBaixa,
    TipoItem,
    TipoLocalizacao,
    TipoManutencao,
    TipoMovimentacao,
)


class Categoria(models.Model):
    codigo = models.CharField(max_length=40, unique=True)
    nome = models.CharField(max_length=120, unique=True)
    descricao = models.TextField(blank=True)
    ativa = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "categorias"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class UnidadeMedida(models.Model):
    nome = models.CharField(max_length=120, unique=True)
    sigla = models.CharField(max_length=20, unique=True)
    permite_fracionamento = models.BooleanField(default=False)

    class Meta:
        verbose_name = "unidade de medida"
        verbose_name_plural = "unidades de medida"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.sigla})"


class Localizacao(models.Model):
    nome = models.CharField(max_length=120)
    codigo = models.CharField(max_length=60, blank=True)
    tipo = models.CharField(max_length=30, choices=TipoLocalizacao.choices)
    localizacao_pai = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="filhas",
    )
    ativa = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["tipo", "nome"]
        constraints = [
            models.UniqueConstraint(
                fields=["tipo", "nome", "localizacao_pai"],
                name="uniq_localizacao_tipo_nome_pai",
            ),
        ]

    def __str__(self):
        return f"{self.get_tipo_display()}: {self.nome}"


class Item(models.Model):
    codigo_interno = models.CharField(max_length=60, unique=True)
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="itens",
    )
    unidade_medida = models.ForeignKey(
        UnidadeMedida,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="itens",
    )
    tipo_item = models.CharField(max_length=40, choices=TipoItem.choices)
    controlado = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return f"{self.codigo_interno} — {self.nome}"


class Equipamento(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name="equipamento")
    numero_serie = models.CharField(max_length=200, unique=True)
    tombamento = models.CharField(max_length=200, unique=True, null=True, blank=True)
    marca = models.CharField(max_length=120, blank=True)
    modelo = models.CharField(max_length=120, blank=True)
    status_operacional = models.CharField(
        max_length=40,
        choices=StatusOperacional.choices,
        default=StatusOperacional.ATIVO,
    )
    data_aquisicao = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.numero_serie


class Estoque(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="estoques")
    localizacao = models.ForeignKey(
        Localizacao, on_delete=models.RESTRICT, related_name="estoques"
    )
    quantidade_disponivel = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    quantidade_reservada = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    nivel_minimo = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    nivel_alerta = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["item", "localizacao"],
                name="uniq_estoque_item_localizacao",
            ),
        ]

    @property
    def abaixo_alerta(self) -> bool:
        return self.quantidade_disponivel <= self.nivel_alerta


class Lote(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="lotes")
    codigo_lote = models.CharField(max_length=120)
    fabricante = models.CharField(max_length=160, blank=True)
    data_fabricacao = models.DateField(null=True, blank=True)
    data_validade = models.DateField(null=True, blank=True)
    quantidade_disponivel = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["item", "codigo_lote"],
                name="uniq_lote_item_codigo",
            ),
        ]
        ordering = ["data_validade", "codigo_lote"]


class Requisicao(models.Model):
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name="requisicoes_solicitadas",
    )
    aprovador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requisicoes_aprovadas",
    )
    setor_solicitante = models.CharField(max_length=160, blank=True)
    finalidade = models.TextField()
    justificativa = models.TextField(blank=True)
    prioridade = models.CharField(
        max_length=20, choices=Prioridade.choices, default=Prioridade.MEDIA
    )
    status = models.CharField(
        max_length=30,
        choices=StatusRequisicao.choices,
        default=StatusRequisicao.ABERTA,
    )
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    data_aprovacao = models.DateTimeField(null=True, blank=True)
    data_atendimento = models.DateTimeField(null=True, blank=True)
    observacao = models.TextField(blank=True)


class RequisicaoItem(models.Model):
    requisicao = models.ForeignKey(
        Requisicao, on_delete=models.CASCADE, related_name="itens"
    )
    item = models.ForeignKey(Item, on_delete=models.RESTRICT, related_name="requisicoes")
    lote_sugerido = models.ForeignKey(
        Lote, on_delete=models.SET_NULL, null=True, blank=True
    )
    quantidade_solicitada = models.DecimalField(max_digits=14, decimal_places=3)
    quantidade_aprovada = models.DecimalField(
        max_digits=14, decimal_places=3, null=True, blank=True
    )
    quantidade_atendida = models.DecimalField(
        max_digits=14, decimal_places=3, null=True, blank=True
    )
    observacao = models.TextField(blank=True)


class OrdemServico(models.Model):
    equipamento = models.ForeignKey(
        Equipamento, on_delete=models.RESTRICT, related_name="ordens_servico"
    )
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ordens_solicitadas",
    )
    tecnico_responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ordens_tecnico",
    )
    descricao_problema = models.TextField()
    descricao_servico = models.TextField(blank=True)
    prioridade = models.CharField(
        max_length=20, choices=Prioridade.choices, default=Prioridade.MEDIA
    )
    status = models.CharField(
        max_length=40,
        choices=StatusOrdemServico.choices,
        default=StatusOrdemServico.ABERTA,
    )
    aberta_em = models.DateTimeField(auto_now_add=True)
    inicio_execucao_em = models.DateTimeField(null=True, blank=True)
    encerrada_em = models.DateTimeField(null=True, blank=True)
    laudo_emitido = models.BooleanField(default=False)


class Manutencao(models.Model):
    ordem_servico = models.ForeignKey(
        OrdemServico, on_delete=models.CASCADE, related_name="manutencoes"
    )
    tipo_manutencao = models.CharField(max_length=40, choices=TipoManutencao.choices)
    descricao = models.TextField(blank=True)
    resultado = models.TextField(blank=True)
    realizada_em = models.DateTimeField(null=True, blank=True)
    custo_estimado = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    proximo_vencimento = models.DateField(null=True, blank=True)


class Inventario(models.Model):
    nome = models.CharField(max_length=160)
    descricao = models.TextField(blank=True)
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inventarios_responsavel",
    )
    status = models.CharField(
        max_length=30,
        choices=StatusInventario.choices,
        default=StatusInventario.ABERTO,
    )
    iniciado_em = models.DateTimeField(auto_now_add=True)
    encerrado_em = models.DateTimeField(null=True, blank=True)


class InventarioItem(models.Model):
    inventario = models.ForeignKey(
        Inventario, on_delete=models.CASCADE, related_name="itens"
    )
    item = models.ForeignKey(Item, on_delete=models.RESTRICT, related_name="inventarios")
    localizacao = models.ForeignKey(
        Localizacao, on_delete=models.SET_NULL, null=True, blank=True
    )
    quantidade_sistema = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    quantidade_contada = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    diferenca = GeneratedField(
        expression=F("quantidade_contada") - F("quantidade_sistema"),
        output_field=models.DecimalField(max_digits=14, decimal_places=3),
        db_persist=True,
    )
    observacao = models.TextField(blank=True)


class Baixa(models.Model):
    item = models.ForeignKey(
        Item, on_delete=models.RESTRICT, null=True, blank=True, related_name="baixas"
    )
    equipamento = models.ForeignKey(
        Equipamento,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="baixas",
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="baixas",
    )
    tipo_baixa = models.CharField(max_length=40, choices=TipoBaixa.choices)
    motivo = models.TextField()
    destino_final = models.TextField(blank=True)
    documento_referencia = models.CharField(max_length=120, blank=True)
    realizada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "baixas"


class Movimentacao(models.Model):
    item = models.ForeignKey(Item, on_delete=models.RESTRICT, related_name="movimentacoes")
    lote = models.ForeignKey(
        Lote, on_delete=models.SET_NULL, null=True, blank=True, related_name="movimentacoes"
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimentacoes",
    )
    requisicao_item = models.ForeignKey(
        RequisicaoItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimentacoes",
    )
    ordem_servico = models.ForeignKey(
        OrdemServico,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimentacoes",
    )
    inventario_item = models.ForeignKey(
        InventarioItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimentacoes",
    )
    baixa = models.ForeignKey(
        Baixa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimentacoes",
    )
    localizacao_origem = models.ForeignKey(
        Localizacao,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimentacoes_origem",
    )
    localizacao_destino = models.ForeignKey(
        Localizacao,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimentacoes_destino",
    )
    tipo_movimentacao = models.CharField(max_length=20, choices=TipoMovimentacao.choices)
    quantidade = models.DecimalField(max_digits=14, decimal_places=3)
    saldo_resultante = models.DecimalField(
        max_digits=14, decimal_places=3, null=True, blank=True
    )
    motivo = models.TextField(blank=True)
    observacao = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Auditoria(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="auditorias",
    )
    acao = models.CharField(max_length=200)
    entidade = models.CharField(max_length=120)
    entidade_id = models.BigIntegerField(null=True, blank=True)
    detalhes = models.JSONField(null=True, blank=True)
    ip_origem = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
