from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"categorias", views.CategoriaViewSet)
router.register(r"unidades", views.UnidadeViewSet)
router.register(r"localizacoes", views.LocalizacaoViewSet)
router.register(r"itens", views.ItemViewSet)
router.register(r"equipamentos", views.EquipamentoViewSet)
router.register(r"estoque", views.EstoqueViewSet)
router.register(r"movimentacoes", views.MovimentacaoViewSet)
router.register(r"requisicoes", views.RequisicaoViewSet)
router.register(r"reservas", views.ReservaViewSet)
router.register(r"ordens", views.OrdemServicoViewSet)
router.register(r"manutencoes", views.ManutencaoViewSet)
router.register(r"inventarios", views.InventarioViewSet)
router.register(r"auditoria", views.AuditoriaViewSet)
router.register(r"usuarios", views.UsuarioViewSet)

urlpatterns = [
    path("", views.lab_manager, name="lab-manager"),
    path("api/", include(router.urls)),
    path("api/auth/csrf/", views.csrf_view, name="auth-csrf"),
    path("api/auth/login/", views.login_view, name="auth-login"),
    path("api/auth/logout/", views.logout_view, name="auth-logout"),
    path("api/auth/me/", views.me_view, name="auth-me"),
    path("api/init/", views.init_view, name="api-init"),
]
