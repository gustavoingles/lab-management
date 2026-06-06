from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    PerfilUsuario, Categoria, Unidade, Localizacao, Item, Equipamento,
    Estoque, Movimentacao, Requisicao, RequisicaoItem, Reserva,
    OrdemServico, ManutencaoAgendada, Inventario, InventarioLinha, AuditoriaLog,
)


class CategoriaSerializer(serializers.ModelSerializer):
    itens = serializers.SerializerMethodField()

    def get_itens(self, obj):
        return obj.item_set.count()

    class Meta:
        model = Categoria
        fields = ["id", "codigo", "nome", "itens"]


class UnidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unidade
        fields = ["id", "sigla", "nome"]


class LocalizacaoSerializer(serializers.ModelSerializer):
    pai = serializers.SerializerMethodField()

    def get_pai(self, obj):
        return obj.pai.nome if obj.pai else None

    class Meta:
        model = Localizacao
        fields = ["id", "nome", "tipo", "pai"]


class ItemSerializer(serializers.ModelSerializer):
    categoria = serializers.CharField(source="categoria.nome")
    unidade = serializers.CharField(source="unidade.sigla")

    class Meta:
        model = Item
        fields = ["id", "codigo", "nome", "tipo", "categoria", "unidade", "controlado"]


class EquipamentoSerializer(serializers.ModelSerializer):
    item = serializers.CharField(source="item.nome")
    local = serializers.CharField(source="localizacao.nome")
    proxManut = serializers.SerializerMethodField()
    os = serializers.SerializerMethodField()

    def get_proxManut(self, obj):
        m = obj.manutencoes.filter(proxima__isnull=False).order_by("proxima").first()
        if m and m.proxima:
            return str(m.proxima)
        return "—"

    def get_os(self, obj):
        return obj.ordens.exclude(status__in=["encerrada", "cancelada"]).count()

    class Meta:
        model = Equipamento
        fields = ["id", "serie", "tombamento", "item", "status", "local", "aquisicao", "proxManut", "os"]


class EstoqueSerializer(serializers.ModelSerializer):
    item = serializers.CharField(source="item.nome")
    codigo = serializers.CharField(source="item.codigo")
    local = serializers.CharField(source="localizacao.nome")
    unidade = serializers.CharField(source="item.unidade.sigla")
    livre = serializers.ReadOnlyField()
    abaixoAlerta = serializers.ReadOnlyField(source="abaixo_alerta")

    class Meta:
        model = Estoque
        fields = ["id", "item", "codigo", "local", "unidade", "total", "reservado", "minimo", "alerta", "livre", "abaixoAlerta"]


class MovimentacaoSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField()
    item = serializers.CharField(source="item.nome")
    qtd = serializers.SerializerMethodField()
    origem = serializers.SerializerMethodField()
    destino = serializers.SerializerMethodField()
    usuario = serializers.SerializerMethodField()
    ref = serializers.CharField(source="referencia")

    def get_data(self, obj):
        return obj.data.strftime("%d/%m %H:%M")

    def get_qtd(self, obj):
        return f"{int(obj.quantidade)} {obj.item.unidade.sigla}"

    def get_origem(self, obj):
        return obj.origem.nome if obj.origem else "—"

    def get_destino(self, obj):
        return obj.destino.nome if obj.destino else "—"

    def get_usuario(self, obj):
        return obj.usuario.get_full_name() or obj.usuario.username

    class Meta:
        model = Movimentacao
        fields = ["id", "data", "tipo", "item", "qtd", "origem", "destino", "usuario", "ref"]


class RequisicaoItemSerializer(serializers.ModelSerializer):
    item = serializers.CharField(source="item.nome")
    unidade = serializers.CharField(source="unidade.sigla")
    reserva = serializers.SerializerMethodField()
    localOpcoes = serializers.SerializerMethodField()

    def get_reserva(self, obj):
        return obj.reserva_local.nome if obj.reserva_local else None

    def get_localOpcoes(self, obj):
        estoques = Estoque.objects.filter(item=obj.item).select_related("localizacao")
        return [e.localizacao.nome for e in estoques if e.livre > 0]

    class Meta:
        model = RequisicaoItem
        fields = ["id", "item", "unidade", "solicitado", "aprovado", "reserva", "atendido", "localOpcoes"]


class RequisicaoSerializer(serializers.ModelSerializer):
    solicitante = serializers.SerializerMethodField()
    criada = serializers.SerializerMethodField()
    itens = RequisicaoItemSerializer(many=True, read_only=True)

    def get_solicitante(self, obj):
        return obj.solicitante.get_full_name() or obj.solicitante.username

    def get_criada(self, obj):
        return obj.criada.strftime("%d/%m/%Y")

    class Meta:
        model = Requisicao
        fields = ["id", "status", "solicitante", "criada", "finalidade", "justificativa", "itens"]


class ReservaSerializer(serializers.ModelSerializer):
    equipamento = serializers.SerializerMethodField()
    serie = serializers.SerializerMethodField()
    solicitante = serializers.SerializerMethodField()
    inicio = serializers.SerializerMethodField()
    fim = serializers.SerializerMethodField()

    def get_equipamento(self, obj):
        return obj.equipamento.item.nome

    def get_serie(self, obj):
        return obj.equipamento.serie

    def get_solicitante(self, obj):
        return obj.solicitante.get_full_name() or obj.solicitante.username

    def get_inicio(self, obj):
        return obj.inicio.strftime("%d/%m %H:%M")

    def get_fim(self, obj):
        return obj.fim.strftime("%d/%m %H:%M")

    class Meta:
        model = Reserva
        fields = ["id", "equipamento", "serie", "solicitante", "inicio", "fim", "status", "finalidade"]


class OrdemServicoSerializer(serializers.ModelSerializer):
    equipamento = serializers.SerializerMethodField()
    serie = serializers.SerializerMethodField()
    abertura = serializers.SerializerMethodField()
    problema = serializers.CharField(source="descricao")
    responsavel = serializers.SerializerMethodField()

    def get_equipamento(self, obj):
        return obj.equipamento.item.nome

    def get_serie(self, obj):
        return obj.equipamento.serie

    def get_abertura(self, obj):
        return obj.abertura.strftime("%d/%m/%Y")

    def get_responsavel(self, obj):
        if obj.responsavel:
            return obj.responsavel.get_full_name() or obj.responsavel.username
        return "—"

    class Meta:
        model = OrdemServico
        fields = ["id", "equipamento", "serie", "status", "prioridade", "abertura", "problema", "responsavel"]


class ManutencaoAgendadaSerializer(serializers.ModelSerializer):
    equipamento = serializers.SerializerMethodField()
    realizada = serializers.SerializerMethodField()
    proximo = serializers.SerializerMethodField()
    os = serializers.SerializerMethodField()
    vencida = serializers.ReadOnlyField()

    def get_equipamento(self, obj):
        return obj.equipamento.item.nome

    def get_realizada(self, obj):
        if obj.ultima_realizada:
            return obj.ultima_realizada.strftime("%d/%m/%Y")
        return "—"

    def get_proximo(self, obj):
        if obj.proxima:
            return obj.proxima.strftime("%d/%m/%Y")
        return "—"

    def get_os(self, obj):
        return obj.ordem.id if obj.ordem else None

    class Meta:
        model = ManutencaoAgendada
        fields = ["id", "equipamento", "tipo", "realizada", "proximo", "os", "vencida"]


class InventarioSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="codigo", read_only=True)
    local = serializers.CharField(source="localizacao.nome")
    responsavel = serializers.SerializerMethodField()
    linhas = serializers.SerializerMethodField()
    divergencias = serializers.SerializerMethodField()
    criado = serializers.SerializerMethodField()

    def get_responsavel(self, obj):
        return obj.responsavel.get_full_name() or obj.responsavel.username

    def get_linhas(self, obj):
        return obj.linhas.count()

    def get_divergencias(self, obj):
        return sum(
            1 for l in obj.linhas.all()
            if l.contado is not None and l.contado != l.esperado
        )

    def get_criado(self, obj):
        return obj.criado.strftime("%d/%m/%Y")

    class Meta:
        model = Inventario
        fields = ["id", "local", "status", "criado", "responsavel", "linhas", "divergencias"]


class InventarioLinhaSerializer(serializers.ModelSerializer):
    item = serializers.CharField(source="item.nome")
    local = serializers.SerializerMethodField()
    sistema = serializers.DecimalField(source="esperado", max_digits=12, decimal_places=2)
    contado = serializers.DecimalField(max_digits=12, decimal_places=2, allow_null=True)
    diff = serializers.ReadOnlyField()

    def get_local(self, obj):
        return obj.localizacao.nome if obj.localizacao else obj.inventario.localizacao.nome

    class Meta:
        model = InventarioLinha
        fields = ["id", "item", "local", "sistema", "contado", "diff"]


class AuditoriaLogSerializer(serializers.ModelSerializer):
    quando = serializers.SerializerMethodField()
    quem = serializers.SerializerMethodField()
    perfil = serializers.SerializerMethodField()

    def get_quando(self, obj):
        return obj.quando.strftime("%d/%m %H:%M")

    def get_quem(self, obj):
        return obj.usuario.get_full_name() or obj.usuario.username

    def get_perfil(self, obj):
        from .models import ROLE_CHOICES
        try:
            role = obj.usuario.perfil.role
            return dict(ROLE_CHOICES).get(role, role)
        except Exception:
            return ""

    class Meta:
        model = AuditoriaLog
        fields = ["id", "quando", "quem", "perfil", "acao", "alvo", "icon", "tone"]


class UsuarioSerializer(serializers.ModelSerializer):
    perfil = serializers.SerializerMethodField()
    tone = serializers.SerializerMethodField()
    ativo = serializers.BooleanField(source="is_active")

    def get_perfil(self, obj):
        from .models import ROLE_CHOICES
        try:
            role = obj.perfil.role
            return dict(ROLE_CHOICES).get(role, role)
        except Exception:
            return "Solicitante"

    def get_tone(self, obj):
        tone_map = {
            "gestor": "violet",
            "almoxarife": "info",
            "solicitante": "neutral",
            "manutencao": "amber",
        }
        try:
            return tone_map.get(obj.perfil.role, "neutral")
        except Exception:
            return "neutral"

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "perfil", "tone", "ativo"]
