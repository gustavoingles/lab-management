from django.db import models
from django.contrib.auth.models import User


ROLE_CHOICES = [
    ("solicitante", "Solicitante"),
    ("almoxarife", "Almoxarife"),
    ("gestor", "Gestor"),
    ("manutencao", "Téc. manutenção"),
]

TIPO_ITEM_CHOICES = [
    ("reagente", "Reagente"),
    ("consumivel", "Consumível"),
    ("epi", "EPI"),
    ("equipamento", "Equipamento"),
    ("peca", "Peça"),
]

STATUS_EQUIPAMENTO_CHOICES = [
    ("ativo", "Ativo"),
    ("em_manutencao", "Em manutenção"),
    ("inativo", "Inativo"),
    ("descartado", "Descartado"),
]

STATUS_REQUISICAO_CHOICES = [
    ("rascunho", "Rascunho"),
    ("aberta", "Aberta"),
    ("em_aprovacao", "Em aprovação"),
    ("aprovada", "Aprovada"),
    ("rejeitada", "Rejeitada"),
    ("atendida", "Atendida"),
    ("cancelada", "Cancelada"),
]

STATUS_OS_CHOICES = [
    ("aberta", "Aberta"),
    ("em_execucao", "Em execução"),
    ("aguardando_pecas", "Aguardando peças"),
    ("encerrada", "Encerrada"),
    ("cancelada", "Cancelada"),
]

STATUS_RESERVA_CHOICES = [
    ("pendente", "Pendente"),
    ("confirmada", "Confirmada"),
    ("cancelada", "Cancelada"),
    ("encerrada", "Encerrada"),
]

STATUS_INVENTARIO_CHOICES = [
    ("aberto", "Aberto"),
    ("em_andamento", "Em andamento"),
    ("encerrado", "Encerrado"),
    ("cancelado", "Cancelado"),
]

TIPO_MOVIMENTACAO_CHOICES = [
    ("entrada", "Entrada"),
    ("saida", "Saída"),
    ("transferencia", "Transferência"),
    ("ajuste", "Ajuste"),
    ("baixa", "Baixa"),
]

PRIORIDADE_CHOICES = [
    ("baixa", "Baixa"),
    ("media", "Média"),
    ("alta", "Alta"),
    ("critica", "Crítica"),
]

TIPO_MANUTENCAO_CHOICES = [
    ("preventiva", "Preventiva"),
    ("corretiva", "Corretiva"),
    ("calibracao", "Calibração"),
    ("verificacao", "Verificação"),
    ("inspecao", "Inspeção"),
]

TIPO_LOCALIZACAO_CHOICES = [
    ("campus", "Campus"),
    ("predio", "Prédio"),
    ("laboratorio", "Laboratório"),
    ("armario", "Armário"),
    ("outro", "Outro"),
]

TONE_CHOICES = [
    ("success", "Sucesso"),
    ("info", "Info"),
    ("amber", "Aviso"),
    ("destructive", "Erro"),
    ("violet", "Roxo"),
    ("neutral", "Neutro"),
]


class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    iniciais = models.CharField(max_length=5)

    def __str__(self):
        return f"{self.usuario.get_full_name()} ({self.role})"


class Categoria(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ["nome"]


class Unidade(models.Model):
    sigla = models.CharField(max_length=10, unique=True)
    nome = models.CharField(max_length=50)

    def __str__(self):
        return self.sigla

    class Meta:
        ordering = ["sigla"]


class Localizacao(models.Model):
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_LOCALIZACAO_CHOICES)
    pai = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="filhos"
    )

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ["nome"]


class Item(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPO_ITEM_CHOICES)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    unidade = models.ForeignKey(Unidade, on_delete=models.PROTECT)
    controlado = models.BooleanField(default=False)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return f"[{self.codigo}] {self.nome}"

    class Meta:
        ordering = ["codigo"]


class Equipamento(models.Model):
    serie = models.CharField(max_length=50, unique=True)
    tombamento = models.CharField(max_length=50, unique=True)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    status = models.CharField(
        max_length=20, choices=STATUS_EQUIPAMENTO_CHOICES, default="ativo"
    )
    localizacao = models.ForeignKey(Localizacao, on_delete=models.PROTECT)
    aquisicao = models.DateField()

    def __str__(self):
        return f"{self.item.nome} ({self.tombamento})"

    class Meta:
        ordering = ["tombamento"]


class Estoque(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    localizacao = models.ForeignKey(Localizacao, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    reservado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    minimo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    alerta = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        unique_together = ("item", "localizacao")

    @property
    def livre(self):
        return float(self.total) - float(self.reservado)

    @property
    def abaixo_alerta(self):
        return self.livre <= float(self.alerta)

    def __str__(self):
        return f"{self.item.nome} @ {self.localizacao.nome}"


class Movimentacao(models.Model):
    tipo = models.CharField(max_length=20, choices=TIPO_MOVIMENTACAO_CHOICES)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    origem = models.ForeignKey(
        Localizacao,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="saidas",
    )
    destino = models.ForeignKey(
        Localizacao,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="entradas",
    )
    quantidade = models.DecimalField(max_digits=12, decimal_places=2)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    data = models.DateTimeField(auto_now_add=True)
    referencia = models.CharField(max_length=100, blank=True)
    obs = models.TextField(blank=True)

    def __str__(self):
        return f"{self.tipo} — {self.item.nome} ({self.quantidade})"

    class Meta:
        ordering = ["-data"]


class Requisicao(models.Model):
    finalidade = models.CharField(max_length=200)
    justificativa = models.TextField(blank=True)
    solicitante = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="requisicoes"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_REQUISICAO_CHOICES, default="aberta"
    )
    prioridade = models.CharField(
        max_length=20, choices=PRIORIDADE_CHOICES, default="media"
    )
    criada = models.DateField(auto_now_add=True)
    aprovador = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="aprovacoes",
    )
    obs_aprovacao = models.TextField(blank=True)

    def __str__(self):
        return f"REQ #{self.id} — {self.finalidade}"

    class Meta:
        ordering = ["-id"]


class RequisicaoItem(models.Model):
    requisicao = models.ForeignKey(
        Requisicao, on_delete=models.CASCADE, related_name="itens"
    )
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    unidade = models.ForeignKey(Unidade, on_delete=models.PROTECT)
    solicitado = models.DecimalField(max_digits=12, decimal_places=2)
    aprovado = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    atendido = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    reserva_local = models.ForeignKey(
        Localizacao, null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ["id"]


class Reserva(models.Model):
    equipamento = models.ForeignKey(
        Equipamento, on_delete=models.CASCADE, related_name="reservas"
    )
    solicitante = models.ForeignKey(User, on_delete=models.PROTECT)
    inicio = models.DateTimeField()
    fim = models.DateTimeField()
    finalidade = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20, choices=STATUS_RESERVA_CHOICES, default="pendente"
    )

    def __str__(self):
        return f"{self.equipamento} — {self.solicitante}"

    class Meta:
        ordering = ["inicio"]


class OrdemServico(models.Model):
    equipamento = models.ForeignKey(
        Equipamento, on_delete=models.CASCADE, related_name="ordens"
    )
    descricao = models.TextField()
    prioridade = models.CharField(
        max_length=20, choices=PRIORIDADE_CHOICES, default="media"
    )
    status = models.CharField(max_length=20, choices=STATUS_OS_CHOICES, default="aberta")
    responsavel = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="ordens"
    )
    abertura = models.DateField(auto_now_add=True)
    previsao = models.DateField(null=True, blank=True)
    conclusao = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"OS #{self.id} — {self.equipamento}"

    class Meta:
        ordering = ["-id"]


class ManutencaoAgendada(models.Model):
    equipamento = models.ForeignKey(
        Equipamento, on_delete=models.CASCADE, related_name="manutencoes"
    )
    tipo = models.CharField(max_length=20, choices=TIPO_MANUTENCAO_CHOICES)
    ultima_realizada = models.DateField(null=True, blank=True)
    proxima = models.DateField(null=True, blank=True)
    ordem = models.ForeignKey(
        OrdemServico, null=True, blank=True, on_delete=models.SET_NULL
    )

    @property
    def vencida(self):
        from django.utils import timezone
        return bool(self.proxima and self.proxima < timezone.now().date())

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.equipamento}"

    class Meta:
        ordering = ["proxima"]


class Inventario(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    localizacao = models.ForeignKey(Localizacao, on_delete=models.PROTECT)
    responsavel = models.ForeignKey(User, on_delete=models.PROTECT)
    status = models.CharField(
        max_length=20, choices=STATUS_INVENTARIO_CHOICES, default="aberto"
    )
    criado = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.codigo

    class Meta:
        ordering = ["-id"]


class InventarioLinha(models.Model):
    inventario = models.ForeignKey(
        Inventario, on_delete=models.CASCADE, related_name="linhas"
    )
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    localizacao = models.ForeignKey(
        Localizacao, null=True, blank=True, on_delete=models.SET_NULL
    )
    esperado = models.DecimalField(max_digits=12, decimal_places=2)
    contado = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    obs = models.TextField(blank=True)

    @property
    def diff(self):
        if self.contado is not None:
            return float(self.contado) - float(self.esperado)
        return None

    class Meta:
        ordering = ["id"]


class AuditoriaLog(models.Model):
    quando = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    acao = models.TextField()
    alvo = models.CharField(max_length=200)
    icon = models.CharField(max_length=50)
    tone = models.CharField(max_length=20, choices=TONE_CHOICES)

    def __str__(self):
        return f"{self.usuario} {self.acao} {self.alvo}"

    class Meta:
        ordering = ["-quando"]
