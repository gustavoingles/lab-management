from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User

from .models import (
    Categoria, Unidade, Localizacao, Item, Equipamento,
    Estoque, Movimentacao, Requisicao, RequisicaoItem,
    Reserva, OrdemServico, ManutencaoAgendada,
    Inventario, InventarioLinha, AuditoriaLog,
)
from .serializers import (
    CategoriaSerializer, UnidadeSerializer, LocalizacaoSerializer,
    ItemSerializer, EquipamentoSerializer, EstoqueSerializer,
    MovimentacaoSerializer, RequisicaoSerializer, ReservaSerializer,
    OrdemServicoSerializer, ManutencaoAgendadaSerializer,
    InventarioSerializer, InventarioLinhaSerializer,
    AuditoriaLogSerializer, UsuarioSerializer,
)


# ------------------------------------------------------------------ app view

def lab_manager(request):
    return render(request, "core/lab_manager.html")


# ------------------------------------------------------------------ auth

@api_view(["GET"])
@permission_classes([AllowAny])
def csrf_view(request):
    return Response({"csrfToken": get_token(request)})


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get("email", "").strip().lower()
    password = request.data.get("password", "")
    try:
        user_obj = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return Response({"detail": "Credenciais inválidas."}, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(request, username=user_obj.username, password=password)
    if user is None:
        return Response({"detail": "Credenciais inválidas."}, status=status.HTTP_401_UNAUTHORIZED)

    login(request, user)

    try:
        role = user.perfil.role
        iniciais = user.perfil.iniciais
    except Exception:
        role = "solicitante"
        iniciais = (user.first_name[:1] + user.last_name[:1]).upper() or user.username[:2].upper()

    return Response({
        "ok": True,
        "role": role,
        "user": {
            "id": user.id,
            "nome": user.get_full_name() or user.username,
            "email": user.email,
            "iniciais": iniciais,
        },
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({"ok": True})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_view(request):
    user = request.user
    try:
        role = user.perfil.role
        iniciais = user.perfil.iniciais
    except Exception:
        role = "solicitante"
        iniciais = (user.first_name[:1] + user.last_name[:1]).upper() or user.username[:2].upper()
    return Response({
        "role": role,
        "user": {
            "id": user.id,
            "nome": user.get_full_name() or user.username,
            "email": user.email,
            "iniciais": iniciais,
        },
    })


# ------------------------------------------------------------------ bootstrap

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def init_view(request):
    """Single endpoint that returns all SPA bootstrap data."""
    return Response({
        "categorias": CategoriaSerializer(Categoria.objects.all(), many=True).data,
        "unidades": UnidadeSerializer(Unidade.objects.all(), many=True).data,
        "localizacoes": LocalizacaoSerializer(Localizacao.objects.all(), many=True).data,
        "itens": ItemSerializer(
            Item.objects.select_related("categoria", "unidade").all(), many=True
        ).data,
        "equipamentos": EquipamentoSerializer(
            Equipamento.objects.select_related("item", "localizacao")
            .prefetch_related("manutencoes", "ordens").all(),
            many=True,
        ).data,
        "estoque": EstoqueSerializer(
            Estoque.objects.select_related("item__unidade", "localizacao").all(), many=True
        ).data,
        "movimentacoes": MovimentacaoSerializer(
            Movimentacao.objects.select_related("item__unidade", "origem", "destino", "usuario").all(),
            many=True,
        ).data,
        "requisicoes": RequisicaoSerializer(
            Requisicao.objects.select_related("solicitante")
            .prefetch_related("itens__item__unidade", "itens__unidade", "itens__reserva_local").all(),
            many=True,
        ).data,
        "reservas": ReservaSerializer(
            Reserva.objects.select_related("equipamento__item", "solicitante").all(), many=True
        ).data,
        "ordens": OrdemServicoSerializer(
            OrdemServico.objects.select_related("equipamento__item", "responsavel").all(), many=True
        ).data,
        "manutencoes": ManutencaoAgendadaSerializer(
            ManutencaoAgendada.objects.select_related("equipamento__item", "ordem").all(), many=True
        ).data,
        "inventarios": InventarioSerializer(
            Inventario.objects.select_related("localizacao", "responsavel")
            .prefetch_related("linhas").all(),
            many=True,
        ).data,
        "inventario_linhas": InventarioLinhaSerializer(
            InventarioLinha.objects.select_related(
                "item", "localizacao", "inventario__localizacao"
            ).all(),
            many=True,
        ).data,
        "auditoria": AuditoriaLogSerializer(
            AuditoriaLog.objects.select_related("usuario__perfil").all(), many=True
        ).data,
    })


# ------------------------------------------------------------------ viewsets

class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]


class UnidadeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Unidade.objects.all()
    serializer_class = UnidadeSerializer
    permission_classes = [IsAuthenticated]


class LocalizacaoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Localizacao.objects.all()
    serializer_class = LocalizacaoSerializer
    permission_classes = [IsAuthenticated]


class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Item.objects.select_related("categoria", "unidade").all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]


class EquipamentoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Equipamento.objects.select_related("item", "localizacao")
        .prefetch_related("manutencoes", "ordens").all()
    )
    serializer_class = EquipamentoSerializer
    permission_classes = [IsAuthenticated]


class EstoqueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Estoque.objects.select_related("item__unidade", "localizacao").all()
    serializer_class = EstoqueSerializer
    permission_classes = [IsAuthenticated]


class MovimentacaoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Movimentacao.objects.select_related(
        "item__unidade", "origem", "destino", "usuario"
    ).all()
    serializer_class = MovimentacaoSerializer
    permission_classes = [IsAuthenticated]


class RequisicaoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Requisicao.objects.select_related("solicitante").prefetch_related(
        "itens__item__unidade", "itens__unidade", "itens__reserva_local"
    ).all()
    serializer_class = RequisicaoSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"])
    def aprovar(self, request, pk=None):
        req = self.get_object()
        if req.status not in ("aberta", "em_aprovacao"):
            return Response({"detail": "Requisição não pode ser aprovada."}, status=400)
        req.status = "aprovada"
        req.aprovador = request.user
        req.save()
        for item in req.itens.all():
            item.aprovado = item.solicitado
            estoque = Estoque.objects.filter(item=item.item).order_by("-total").first()
            if estoque:
                item.reserva_local = estoque.localizacao
            item.save()
        AuditoriaLog.objects.create(
            usuario=request.user, acao="aprovou",
            alvo=f"Requisição #{req.id}", icon="check-circle-2", tone="success",
        )
        return Response(RequisicaoSerializer(req).data)

    @action(detail=True, methods=["post"])
    def rejeitar(self, request, pk=None):
        req = self.get_object()
        if req.status not in ("aberta", "em_aprovacao", "aprovada"):
            return Response({"detail": "Requisição não pode ser rejeitada."}, status=400)
        req.status = "rejeitada"
        req.aprovador = request.user
        req.obs_aprovacao = request.data.get("obs", "")
        req.save()
        AuditoriaLog.objects.create(
            usuario=request.user, acao="rejeitou",
            alvo=f"Requisição #{req.id}", icon="x-circle", tone="destructive",
        )
        return Response(RequisicaoSerializer(req).data)

    @action(detail=True, methods=["post"])
    def atender(self, request, pk=None):
        req = self.get_object()
        if req.status != "aprovada":
            return Response({"detail": "Requisição não está aprovada."}, status=400)
        item_id = request.data.get("item_id")
        if item_id:
            try:
                ri = req.itens.get(id=item_id)
                ri.atendido = ri.aprovado
                ri.save()
            except RequisicaoItem.DoesNotExist:
                return Response({"detail": "Item não encontrado."}, status=404)
        if req.itens.filter(atendido__isnull=True).count() == 0:
            req.status = "atendida"
            req.save()
            AuditoriaLog.objects.create(
                usuario=request.user, acao="atendeu",
                alvo=f"Requisição #{req.id}", icon="package-check", tone="success",
            )
        return Response(RequisicaoSerializer(req).data)


class ReservaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Reserva.objects.select_related("equipamento__item", "solicitante").all()
    serializer_class = ReservaSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"])
    def confirmar(self, request, pk=None):
        reserva = self.get_object()
        if reserva.status != "pendente":
            return Response({"detail": "Reserva não está pendente."}, status=400)
        reserva.status = "confirmada"
        reserva.save()
        AuditoriaLog.objects.create(
            usuario=request.user, acao="confirmou reserva de",
            alvo=reserva.equipamento.item.nome, icon="check-circle-2", tone="success",
        )
        return Response(ReservaSerializer(reserva).data)


class OrdemServicoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OrdemServico.objects.select_related("equipamento__item", "responsavel").all()
    serializer_class = OrdemServicoSerializer
    permission_classes = [IsAuthenticated]


class ManutencaoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ManutencaoAgendada.objects.select_related("equipamento__item", "ordem").all()
    serializer_class = ManutencaoAgendadaSerializer
    permission_classes = [IsAuthenticated]


class InventarioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Inventario.objects.select_related("localizacao", "responsavel")
        .prefetch_related("linhas").all()
    )
    serializer_class = InventarioSerializer
    permission_classes = [IsAuthenticated]


class AuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditoriaLog.objects.select_related("usuario__perfil").all()
    serializer_class = AuditoriaLogSerializer
    permission_classes = [IsAuthenticated]


class UsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.select_related("perfil").order_by("first_name")
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]
