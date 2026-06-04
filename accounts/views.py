from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.models import Perfil, SolicitacaoAlteracaoPerfil
from accounts.permissions import CanManageUsers, PERFIS_GESTAO, usuario_tem_perfil
from accounts.serializers import (
    PerfilSerializer,
    RegisterSerializer,
    SolicitacaoAlteracaoPerfilCreateSerializer,
    SolicitacaoAlteracaoPerfilSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from accounts.services.solicitacao_perfil import (
    aprovar_solicitacao,
    cancelar_solicitacao,
    rejeitar_solicitacao,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class PerfilListView(generics.ListAPIView):
    queryset = Perfil.objects.filter(ativo=True).order_by("nome")
    serializer_class = PerfilSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageUsers]


class PerfilDisponiveisListView(generics.ListAPIView):
    """Perfis que o usuário pode solicitar (exceto o atual)."""

    serializer_class = PerfilSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Perfil.objects.filter(ativo=True).exclude(
            pk=self.request.user.perfil_id
        ).order_by("nome")


class SolicitacaoAlteracaoPerfilViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_serializer_class(self):
        if self.action == "create":
            return SolicitacaoAlteracaoPerfilCreateSerializer
        return SolicitacaoAlteracaoPerfilSerializer

    def get_queryset(self):
        qs = SolicitacaoAlteracaoPerfil.objects.select_related(
            "solicitante",
            "perfil_atual",
            "perfil_solicitado",
            "revisado_por",
        )
        if usuario_tem_perfil(self.request.user, *PERFIS_GESTAO):
            if status_param := self.request.query_params.get("status"):
                qs = qs.filter(status=status_param)
            return qs.order_by("-criada_em")
        return qs.filter(solicitante=self.request.user).order_by("-criada_em")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            obj = serializer.save()
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages) from exc
        return Response(
            SolicitacaoAlteracaoPerfilSerializer(obj).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def aprovar(self, request, pk=None):
        if not usuario_tem_perfil(request.user, *PERFIS_GESTAO):
            return Response(status=status.HTTP_403_FORBIDDEN)
        solicitacao = self.get_object()
        try:
            aprovar_solicitacao(
                revisor=request.user,
                solicitacao=solicitacao,
                resposta=request.data.get("resposta_revisao", ""),
            )
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages) from exc
        return Response(SolicitacaoAlteracaoPerfilSerializer(solicitacao).data)

    @action(detail=True, methods=["post"])
    def rejeitar(self, request, pk=None):
        if not usuario_tem_perfil(request.user, *PERFIS_GESTAO):
            return Response(status=status.HTTP_403_FORBIDDEN)
        solicitacao = self.get_object()
        try:
            rejeitar_solicitacao(
                revisor=request.user,
                solicitacao=solicitacao,
                resposta=request.data.get("resposta_revisao", ""),
            )
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages) from exc
        return Response(SolicitacaoAlteracaoPerfilSerializer(solicitacao).data)

    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        solicitacao = self.get_object()
        try:
            cancelar_solicitacao(usuario=request.user, solicitacao=solicitacao)
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages) from exc
        return Response(SolicitacaoAlteracaoPerfilSerializer(solicitacao).data)


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related("perfil").order_by("nome")
    permission_classes = [permissions.IsAuthenticated, CanManageUsers]
    http_method_names = ["get", "patch", "head", "options"]

    def get_serializer_class(self):
        if self.action in ("partial_update", "update"):
            return UserUpdateSerializer
        return UserSerializer

    def get_queryset(self):
        qs = User.objects.select_related("perfil").order_by("nome")
        if perfil := self.request.query_params.get("perfil"):
            qs = qs.filter(perfil__codigo=perfil)
        if ativo := self.request.query_params.get("ativo"):
            qs = qs.filter(is_active=ativo.lower() == "true")
        return qs

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response(UserSerializer(self.get_object()).data)


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["nome"] = user.nome
        token["perfil"] = user.perfil.codigo
        return token


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer
