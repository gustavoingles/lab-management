from django.urls import include, path
from rest_framework.routers import DefaultRouter

from inventory import views

router = DefaultRouter()
router.register("categorias", views.CategoriaViewSet)
router.register("unidades-medida", views.UnidadeMedidaViewSet)
router.register("localizacoes", views.LocalizacaoViewSet)
router.register("itens", views.ItemViewSet)
router.register("equipamentos", views.EquipamentoViewSet)
router.register("estoques", views.EstoqueViewSet)
router.register("lotes", views.LoteViewSet)
router.register("movimentacoes", views.MovimentacaoViewSet)
router.register("requisicoes", views.RequisicaoViewSet)
router.register("requisicao-itens", views.RequisicaoItemViewSet)
router.register("ordens-servico", views.OrdemServicoViewSet)
router.register("manutencoes", views.ManutencaoViewSet)
router.register("inventarios", views.InventarioViewSet)
router.register("inventario-itens", views.InventarioItemViewSet)
router.register("baixas", views.BaixaViewSet)
router.register("auditorias", views.AuditoriaViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
