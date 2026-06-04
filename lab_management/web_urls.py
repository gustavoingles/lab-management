from django.urls import path

from accounts import web_views as accounts_web_views
from lab_management import web_crud, web_views

app_name = "app"

urlpatterns = [
    path("", web_views.DashboardView.as_view(), name="dashboard"),
    # Categorias
    path("categorias/", web_views.CategoriaListView.as_view(), name="categorias"),
    path("categorias/nova/", web_views.CategoriaCreateView.as_view(), name="categoria_nova"),
    path(
        "categorias/<int:pk>/editar/",
        web_crud.CategoriaUpdateView.as_view(),
        name="categoria_editar",
    ),
    path(
        "categorias/<int:pk>/excluir/",
        web_crud.CategoriaDeleteView.as_view(),
        name="categoria_excluir",
    ),
    # Unidades de medida
    path(
        "unidades-medida/",
        web_crud.UnidadeMedidaListView.as_view(),
        name="unidades_medida",
    ),
    path(
        "unidades-medida/nova/",
        web_crud.UnidadeMedidaCreateView.as_view(),
        name="unidade_medida_nova",
    ),
    path(
        "unidades-medida/<int:pk>/editar/",
        web_crud.UnidadeMedidaUpdateView.as_view(),
        name="unidade_medida_editar",
    ),
    path(
        "unidades-medida/<int:pk>/excluir/",
        web_crud.UnidadeMedidaDeleteView.as_view(),
        name="unidade_medida_excluir",
    ),
    # Itens
    path("itens/", web_views.ItemListView.as_view(), name="itens"),
    path("itens/novo/", web_views.ItemCreateView.as_view(), name="item_novo"),
    path("itens/<int:pk>/editar/", web_crud.ItemUpdateView.as_view(), name="item_editar"),
    path("itens/<int:pk>/excluir/", web_crud.ItemDeleteView.as_view(), name="item_excluir"),
    # Equipamentos
    path("equipamentos/", web_views.EquipamentoListView.as_view(), name="equipamentos"),
    path(
        "equipamentos/novo/",
        web_views.EquipamentoCreateView.as_view(),
        name="equipamento_novo",
    ),
    path(
        "equipamentos/<int:pk>/editar/",
        web_crud.EquipamentoUpdateView.as_view(),
        name="equipamento_editar",
    ),
    path(
        "equipamentos/<int:pk>/excluir/",
        web_crud.EquipamentoDeleteView.as_view(),
        name="equipamento_excluir",
    ),
    # Localizações
    path("localizacoes/", web_views.LocalizacaoListView.as_view(), name="localizacoes"),
    path(
        "localizacoes/nova/",
        web_views.LocalizacaoCreateView.as_view(),
        name="localizacao_nova",
    ),
    path(
        "localizacoes/<int:pk>/editar/",
        web_crud.LocalizacaoUpdateView.as_view(),
        name="localizacao_editar",
    ),
    path(
        "localizacoes/<int:pk>/excluir/",
        web_crud.LocalizacaoDeleteView.as_view(),
        name="localizacao_excluir",
    ),
    # Lotes
    path("lotes/", web_crud.LoteListView.as_view(), name="lotes"),
    path("lotes/novo/", web_crud.LoteCreateView.as_view(), name="lote_novo"),
    path("lotes/<int:pk>/editar/", web_crud.LoteUpdateView.as_view(), name="lote_editar"),
    path("lotes/<int:pk>/excluir/", web_crud.LoteDeleteView.as_view(), name="lote_excluir"),
    # Estoque
    path("estoques/", web_views.EstoqueListView.as_view(), name="estoques"),
    path(
        "estoques/<int:pk>/editar/",
        web_crud.EstoqueUpdateView.as_view(),
        name="estoque_editar",
    ),
    # Movimentações
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
    # Requisições
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
    # Ordens de serviço
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
        "ordens-servico/<int:pk>/",
        web_crud.OrdemServicoDetailView.as_view(),
        name="ordem_servico_detalhe",
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
    path(
        "ordens-servico/<int:os_pk>/manutencoes/nova/",
        web_crud.ManutencaoCreateView.as_view(),
        name="ordem_servico_manutencao_nova",
    ),
    # Manutenções
    path("manutencoes/", web_crud.ManutencaoListView.as_view(), name="manutencoes"),
    path(
        "manutencoes/nova/",
        web_crud.ManutencaoCreateView.as_view(),
        name="manutencao_nova",
    ),
    path(
        "manutencoes/<int:pk>/editar/",
        web_crud.ManutencaoUpdateView.as_view(),
        name="manutencao_editar",
    ),
    path(
        "manutencoes/<int:pk>/excluir/",
        web_crud.ManutencaoDeleteView.as_view(),
        name="manutencao_excluir",
    ),
    # Inventários
    path("inventarios/", web_crud.InventarioListView.as_view(), name="inventarios"),
    path(
        "inventarios/novo/",
        web_crud.InventarioCreateView.as_view(),
        name="inventario_novo",
    ),
    path(
        "inventarios/<int:pk>/",
        web_crud.InventarioDetailView.as_view(),
        name="inventario_detalhe",
    ),
    path(
        "inventarios/<int:pk>/editar/",
        web_crud.InventarioUpdateView.as_view(),
        name="inventario_editar",
    ),
    path(
        "inventarios/<int:pk>/excluir/",
        web_crud.InventarioDeleteView.as_view(),
        name="inventario_excluir",
    ),
    path(
        "inventarios/<int:pk>/itens/",
        web_crud.InventarioItemAddView.as_view(),
        name="inventario_item_add",
    ),
    path(
        "inventario-itens/<int:pk>/excluir/",
        web_crud.InventarioItemDeleteView.as_view(),
        name="inventario_item_excluir",
    ),
    # Baixas
    path("baixas/", web_crud.BaixaListView.as_view(), name="baixas"),
    path("baixas/nova/", web_crud.BaixaCreateView.as_view(), name="baixa_nova"),
    path("baixas/<int:pk>/editar/", web_crud.BaixaUpdateView.as_view(), name="baixa_editar"),
    path("baixas/<int:pk>/excluir/", web_crud.BaixaDeleteView.as_view(), name="baixa_excluir"),
    # Reservas de equipamento
    path(
        "reservas-equipamento/",
        web_crud.ReservaEquipamentoListView.as_view(),
        name="reservas_equipamento",
    ),
    path(
        "reservas-equipamento/nova/",
        web_crud.ReservaEquipamentoCreateView.as_view(),
        name="reserva_equipamento_nova",
    ),
    path(
        "reservas-equipamento/<int:pk>/aprovar/",
        web_crud.ReservaEquipamentoAprovarView.as_view(),
        name="reserva_equipamento_aprovar",
    ),
    path(
        "reservas-equipamento/<int:pk>/cancelar/",
        web_crud.ReservaEquipamentoCancelarView.as_view(),
        name="reserva_equipamento_cancelar",
    ),
    path(
        "reservas-equipamento/<int:pk>/encerrar/",
        web_crud.ReservaEquipamentoEncerrarView.as_view(),
        name="reserva_equipamento_encerrar",
    ),
    # Auditoria e usuários
    path("auditoria/", web_views.AuditoriaListView.as_view(), name="auditorias"),
    path("usuarios/", web_views.UsuarioListView.as_view(), name="usuarios"),
    path(
        "usuarios/<int:pk>/editar/",
        web_views.UsuarioUpdateView.as_view(),
        name="usuario_editar",
    ),
    # Solicitações de perfil
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
