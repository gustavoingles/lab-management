from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import (
    EmailTokenObtainPairView,
    MeView,
    PerfilDisponiveisListView,
    PerfilListView,
    RegisterView,
    SolicitacaoAlteracaoPerfilViewSet,
    UsuarioViewSet,
)

router = DefaultRouter()
router.register("usuarios", UsuarioViewSet, basename="usuario")
router.register(
    "solicitacoes-perfil",
    SolicitacaoAlteracaoPerfilViewSet,
    basename="solicitacao_perfil",
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="api_register"),
    path("token/", EmailTokenObtainPairView.as_view(), name="api_token"),
    path("token/refresh/", TokenRefreshView.as_view(), name="api_token_refresh"),
    path("me/", MeView.as_view(), name="api_me"),
    path("perfis/", PerfilListView.as_view(), name="api_perfis"),
    path(
        "perfis-disponiveis/",
        PerfilDisponiveisListView.as_view(),
        name="api_perfis_disponiveis",
    ),
    path("", include(router.urls)),
]
