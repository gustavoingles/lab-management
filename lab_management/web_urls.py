from django.urls import path

from accounts import web_views as accounts_web_views
from lab_management import web_views

app_name = "app"

urlpatterns = [
    path("", web_views.DashboardView.as_view(), name="dashboard"),
    path("categorias/", web_views.CategoriaListView.as_view(), name="categorias"),
    path("categorias/nova/", web_views.CategoriaCreateView.as_view(), name="categoria_nova"),
    path("itens/", web_views.ItemListView.as_view(), name="itens"),
    path("itens/novo/", web_views.ItemCreateView.as_view(), name="item_novo"),
    path("equipamentos/", web_views.EquipamentoListView.as_view(), name="equipamentos"),
    path(
        "equipamentos/novo/",
        web_views.EquipamentoCreateView.as_view(),
        name="equipamento_novo",
    ),
    path("localizacoes/", web_views.LocalizacaoListView.as_view(), name="localizacoes"),
    path(
        "localizacoes/nova/",
        web_views.LocalizacaoCreateView.as_view(),
        name="localizacao_nova",
    ),
    path("estoques/", web_views.EstoqueListView.as_view(), name="estoques"),
    path(
        "movimentacoes/",
        web_views.MovimentacaoListView.as_view(),
        name="movimentacoes",
    ),
    path(
        "movimentacoes/nova/",
        web_views.MovimentacaoCreateView.as_view(),
        name="movimentacao_nova",
    ),
    path("requisicoes/", web_views.RequisicaoListView.as_view(), name="requisicoes"),
    path(
        "requisicoes/nova/",
        web_views.RequisicaoCreateView.as_view(),
        name="requisicao_nova",
    ),
    path(
        "requisicoes/<int:pk>/",
        web_views.RequisicaoDetailView.as_view(),
        name="requisicao_detalhe",
    ),
    path(
        "requisicoes/<int:pk>/itens/",
        web_views.RequisicaoItemAddView.as_view(),
        name="requisicao_item_add",
    ),
    path(
        "requisicoes/<int:pk>/aprovar/",
        web_views.RequisicaoAprovarView.as_view(),
        name="requisicao_aprovar",
    ),
    path(
        "requisicoes/<int:pk>/rejeitar/",
        web_views.RequisicaoRejeitarView.as_view(),
        name="requisicao_rejeitar",
    ),
    path(
        "requisicoes/<int:pk>/itens/<int:item_pk>/atender/",
        web_views.RequisicaoAtenderItemView.as_view(),
        name="requisicao_atender_item",
    ),
    path(
        "ordens-servico/",
        web_views.OrdemServicoListView.as_view(),
        name="ordens_servico",
    ),
    path(
        "ordens-servico/nova/",
        web_views.OrdemServicoCreateView.as_view(),
        name="ordem_servico_nova",
    ),
    path(
        "ordens-servico/<int:pk>/iniciar/",
        web_views.OrdemServicoIniciarView.as_view(),
        name="ordem_servico_iniciar",
    ),
    path(
        "ordens-servico/<int:pk>/encerrar/",
        web_views.OrdemServicoEncerrarView.as_view(),
        name="ordem_servico_encerrar",
    ),
    path("auditoria/", web_views.AuditoriaListView.as_view(), name="auditorias"),
    path("usuarios/", web_views.UsuarioListView.as_view(), name="usuarios"),
    path(
        "usuarios/<int:pk>/editar/",
        web_views.UsuarioUpdateView.as_view(),
        name="usuario_editar",
    ),
    path(
        "meu-perfil/solicitacao/",
        accounts_web_views.MinhaSolicitacaoPerfilView.as_view(),
        name="minha_solicitacao_perfil",
    ),
    path(
        "meu-perfil/solicitacao/nova/",
        accounts_web_views.SolicitacaoAlteracaoPerfilCreateView.as_view(),
        name="solicitacao_perfil_nova",
    ),
    path(
        "meu-perfil/solicitacao/<int:pk>/cancelar/",
        accounts_web_views.SolicitacaoAlteracaoPerfilCancelarView.as_view(),
        name="solicitacao_perfil_cancelar",
    ),
    path(
        "solicitacoes-perfil/",
        accounts_web_views.SolicitacaoAlteracaoPerfilAdminListView.as_view(),
        name="solicitacoes_perfil_admin",
    ),
    path(
        "solicitacoes-perfil/<int:pk>/aprovar/",
        accounts_web_views.SolicitacaoAlteracaoPerfilAprovarView.as_view(),
        name="solicitacao_perfil_aprovar",
    ),
    path(
        "solicitacoes-perfil/<int:pk>/rejeitar/",
        accounts_web_views.SolicitacaoAlteracaoPerfilRejeitarView.as_view(),
        name="solicitacao_perfil_rejeitar",
    ),
]
