from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import (
    CanApproveRequisicoes,
    CanManageBaixas,
    CanManageCatalog,
    CanManageInventario,
    CanManageOrdensServico,
    CanManageRequisicoes,
    CanManageStock,
    CanViewAuditoria,
)
from inventory.models import (
    Auditoria,
    Baixa,
    Categoria,
    Equipamento,
    Estoque,
    Inventario,
    InventarioItem,
    Item,
    Localizacao,
    Lote,
    Manutencao,
    Movimentacao,
    OrdemServico,
    Requisicao,
    RequisicaoItem,
    UnidadeMedida,
)
from inventory.serializers import (
    AtenderRequisicaoItemSerializer,
    AuditoriaSerializer,
    BaixaSerializer,
    CategoriaSerializer,
    EncerrarOrdemServicoSerializer,
    EquipamentoSerializer,
    EstoqueSerializer,
    InventarioItemSerializer,
    InventarioSerializer,
    ItemSerializer,
    LocalizacaoSerializer,
    LoteSerializer,
    ManutencaoSerializer,
    MovimentacaoCreateSerializer,
    MovimentacaoSerializer,
    OrdemServicoSerializer,
    RequisicaoItemCreateSerializer,
    RequisicaoItemSerializer,
    RequisicaoSerializer,
    UnidadeMedidaSerializer,
)
from inventory.services import (
    aprovar_requisicao,
    atender_requisicao_item,
    encerrar_ordem_servico,
    iniciar_ordem_servico,
    registrar_auditoria,
    registrar_movimentacao,
    rejeitar_requisicao,
)


class AuditMixin:
    entidade: str = ""

    def perform_create(self, serializer):
        instance = serializer.save()
        registrar_auditoria(
            request=self.request,
            acao=f"{self.entidade}.criar",
            entidade=self.entidade,
            entidade_id=instance.pk,
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        registrar_auditoria(
            request=self.request,
            acao=f"{self.entidade}.atualizar",
            entidade=self.entidade,
            entidade_id=instance.pk,
        )

    def perform_destroy(self, instance):
        pk = instance.pk
        instance.delete()
        registrar_auditoria(
            request=self.request,
            acao=f"{self.entidade}.excluir",
            entidade=self.entidade,
            entidade_id=pk,
        )


class CategoriaViewSet(AuditMixin, viewsets.ModelViewSet):
    entidade = "categoria"
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated, CanManageCatalog]


class UnidadeMedidaViewSet(AuditMixin, viewsets.ModelViewSet):
    entidade = "unidade_medida"
    queryset = UnidadeMedida.objects.all()
    serializer_class = UnidadeMedidaSerializer
    permission_classes = [IsAuthenticated, CanManageCatalog]


class LocalizacaoViewSet(AuditMixin, viewsets.ModelViewSet):
    entidade = "localizacao"
    queryset = Localizacao.objects.select_related("localizacao_pai")
    serializer_class = LocalizacaoSerializer
    permission_classes = [IsAuthenticated, CanManageCatalog]


class ItemViewSet(AuditMixin, viewsets.ModelViewSet):
    entidade = "item"
    queryset = Item.objects.select_related("categoria", "unidade_medida")
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated, CanManageCatalog]

    def get_queryset(self):
        qs = super().get_queryset()
        if tipo := self.request.query_params.get("tipo_item"):
            qs = qs.filter(tipo_item=tipo)
        if ativo := self.request.query_params.get("ativo"):
            qs = qs.filter(ativo=ativo.lower() == "true")
        return qs


class EquipamentoViewSet(AuditMixin, viewsets.ModelViewSet):
    entidade = "equipamento"
    queryset = Equipamento.objects.select_related("item")
    serializer_class = EquipamentoSerializer
    permission_classes = [IsAuthenticated, CanManageCatalog]

    def get_queryset(self):
        qs = super().get_queryset()
        if status_op := self.request.query_params.get("status_operacional"):
            qs = qs.filter(status_operacional=status_op)
        return qs


class EstoqueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Estoque.objects.select_related("item", "localizacao")
    serializer_class = EstoqueSerializer
    permission_classes = [IsAuthenticated, CanManageStock]

    @action(detail=False, methods=["get"], url_path="alertas")
    def alertas(self, request):
        alertas = [e for e in self.get_queryset() if e.abaixo_alerta]
        return Response(EstoqueSerializer(alertas, many=True).data)


class LoteViewSet(AuditMixin, viewsets.ModelViewSet):
    entidade = "lote"
    queryset = Lote.objects.select_related("item")
    serializer_class = LoteSerializer
    permission_classes = [IsAuthenticated, CanManageStock]

    def get_queryset(self):
        qs = super().get_queryset()
        if item_id := self.request.query_params.get("item"):
            qs = qs.filter(item_id=item_id)
        return qs.order_by("data_validade")


class MovimentacaoViewSet(viewsets.ModelViewSet):
    queryset = Movimentacao.objects.select_related("item", "lote", "usuario")
    serializer_class = MovimentacaoSerializer
    permission_classes = [IsAuthenticated, CanManageStock]
    http_method_names = ["get", "post", "head", "options"]

    def create(self, request, *args, **kwargs):
        input_ser = MovimentacaoCreateSerializer(data=request.data)
        input_ser.is_valid(raise_exception=True)
        data = input_ser.validated_data
        item = Item.objects.get(pk=data["item_id"])
        lote = None
        if data.get("lote_id"):
            lote = Lote.objects.get(pk=data["lote_id"])
        try:
            mov = registrar_movimentacao(
                request=request,
                item=item,
                lote=lote,
                **{k: v for k, v in data.items() if k not in ("item_id", "lote_id")},
            )
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages) from exc
        return Response(
            MovimentacaoSerializer(mov).data,
            status=status.HTTP_201_CREATED,
        )


class RequisicaoViewSet(AuditMixin, viewsets.ModelViewSet):
    entidade = "requisicao"
    queryset = Requisicao.objects.prefetch_related("itens").select_related(
        "solicitante", "aprovador"
    )
    serializer_class = RequisicaoSerializer
    permission_classes = [IsAuthenticated, CanManageRequisicoes]

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, CanApproveRequisicoes],
    )
    def aprovar(self, request, pk=None):
        requisicao = self.get_object()
        try:
            aprovar_requisicao(request=request, requisicao=requisicao)
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages) from exc
        return Response(RequisicaoSerializer(requisicao).data)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, CanApproveRequisicoes],
    )
    def rejeitar(self, request, pk=None):
        requisicao = self.get_object()
        try:
            rejeitar_requisicao(
                request=request,
                requisicao=requisicao,
                motivo=request.data.get("motivo", ""),
            )
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages) from exc
        return Response(RequisicaoSerializer(requisicao).data)


class RequisicaoItemViewSet(AuditMixin, viewsets.ModelViewSet):
    entidade = "requisicao_item"
    queryset = RequisicaoItem.objects.select_related("requisicao", "item", "lote_sugerido")
    permission_classes = [IsAuthenticated, CanManageRequisicoes]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return RequisicaoItemCreateSerializer
        return RequisicaoItemSerializer

    @action(detail=True, methods=["post"], url_path="atender")
    def atender(self, request, pk=None):
        linha = self.get_object()
        ser = AtenderRequisicaoItemSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            atender_requisicao_item(request=request, linha=linha, **ser.validated_data)
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages) from exc
        return Response(RequisicaoItemSerializer(linha).data)


class OrdemServicoViewSet(AuditMixin, viewsets.ModelViewSet):
    entidade = "ordem_servico"
    queryset = OrdemServico.objects.select_related(
        "equipamento", "solicitante", "tecnico_responsavel"
    )
    serializer_class = OrdemServicoSerializer
    permission_classes = [IsAuthenticated, CanManageOrdensServico]

    def perform_create(self, serializer):
        instance = serializer.save(solicitante=self.request.user)
        registrar_auditoria(
            request=self.request,
            acao="ordem_servico.criar",
            entidade="ordem_servico",
            entidade_id=instance.pk,
        )

    @action(detail=True, methods=["post"])
    def iniciar(self, request, pk=None):
        ordem = self.get_object()
        try:
            iniciar_ordem_servico(request=request, ordem=ordem)
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages) from exc
        return Response(OrdemServicoSerializer(ordem).data)

    @action(detail=True, methods=["post"])
    def encerrar(self, request, pk=None):
        ordem = self.get_object()
        ser = EncerrarOrdemServicoSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            encerrar_ordem_servico(request=request, ordem=ordem, **ser.validated_data)
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages) from exc
        return Response(OrdemServicoSerializer(ordem).data)


class ManutencaoViewSet(AuditMixin, viewsets.ModelViewSet):
    entidade = "manutencao"
    queryset = Manutencao.objects.select_related("ordem_servico")
    serializer_class = ManutencaoSerializer
    permission_classes = [IsAuthenticated, CanManageOrdensServico]


class InventarioViewSet(AuditMixin, viewsets.ModelViewSet):
    entidade = "inventario"
    queryset = Inventario.objects.select_related("responsavel")
    serializer_class = InventarioSerializer
    permission_classes = [IsAuthenticated, CanManageInventario]


class InventarioItemViewSet(AuditMixin, viewsets.ModelViewSet):
    entidade = "inventario_item"
    queryset = InventarioItem.objects.select_related("inventario", "item", "localizacao")
    serializer_class = InventarioItemSerializer
    permission_classes = [IsAuthenticated, CanManageInventario]


class BaixaViewSet(AuditMixin, viewsets.ModelViewSet):
    entidade = "baixa"
    queryset = Baixa.objects.select_related("item", "equipamento", "usuario")
    serializer_class = BaixaSerializer
    permission_classes = [IsAuthenticated, CanManageBaixas]


class AuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Auditoria.objects.select_related("usuario")
    serializer_class = AuditoriaSerializer
    permission_classes = [IsAuthenticated, CanViewAuditoria]
