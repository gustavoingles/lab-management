from accounts.permissions import (
    PERFIL_ALMOXARIFE,
    PERFIS_GESTAO,
    PERFIS_ESTOQUE,
    PERFIS_SOLICITACAO,
    PERFIS_MANUTENCAO,
    usuario_tem_perfil,
)


def app_navigation(request):
    if not request.user.is_authenticated:
        return {"app_nav": []}

    user = request.user
    nav = [{"label": "Início", "url_name": "app:dashboard", "icon": "layout-dashboard"}]

    if usuario_tem_perfil(
        user, *PERFIS_ESTOQUE, *PERFIS_SOLICITACAO, *PERFIS_MANUTENCAO, "auditor", "fiscal"
    ):
        nav.extend(
            [
                {"label": "Catálogo", "url_name": "app:itens", "icon": "boxes"},
                {"label": "Equipamentos", "url_name": "app:equipamentos", "icon": "cpu"},
            ]
        )

    if usuario_tem_perfil(user, *PERFIS_ESTOQUE):
        nav.extend(
            [
                {"label": "Localizações", "url_name": "app:localizacoes", "icon": "map-pin"},
                {"label": "Unidades", "url_name": "app:unidades_medida", "icon": "ruler"},
                {"label": "Lotes", "url_name": "app:lotes", "icon": "package"},
                {"label": "Estoque", "url_name": "app:estoques", "icon": "warehouse"},
                {
                    "label": "Movimentações",
                    "url_name": "app:movimentacao_nova",
                    "icon": "arrow-left-right",
                },
                {"label": "Inventários", "url_name": "app:inventarios", "icon": "clipboard-check"},
            ]
        )

    if usuario_tem_perfil(user, *PERFIS_GESTAO, PERFIL_ALMOXARIFE):
        nav.append({"label": "Baixas", "url_name": "app:baixas", "icon": "trash-2"})

    if usuario_tem_perfil(user, *PERFIS_ESTOQUE, *PERFIS_SOLICITACAO):
        nav.extend(
            [
                {
                    "label": "Requisições",
                    "url_name": "app:requisicoes",
                    "icon": "clipboard-list",
                },
                {
                    "label": "Reservas",
                    "url_name": "app:reservas_equipamento",
                    "icon": "calendar",
                },
            ]
        )

    if usuario_tem_perfil(user, *PERFIS_GESTAO, *PERFIS_MANUTENCAO):
        nav.extend(
            [
                {
                    "label": "Ordens de serviço",
                    "url_name": "app:ordens_servico",
                    "icon": "wrench",
                },
                {"label": "Manutenções", "url_name": "app:manutencoes", "icon": "settings"},
            ]
        )

    if usuario_tem_perfil(user, *PERFIS_GESTAO, "auditor", "fiscal"):
        nav.append(
            {"label": "Auditoria", "url_name": "app:auditorias", "icon": "shield-check"}
        )

    nav.append(
        {"label": "Meu perfil", "url_name": "app:minha_solicitacao_perfil", "icon": "user"}
    )

    if usuario_tem_perfil(user, *PERFIS_GESTAO):
        nav.extend(
            [
                {"label": "Usuários", "url_name": "app:usuarios", "icon": "users"},
                {
                    "label": "Solicitações de perfil",
                    "url_name": "app:solicitacoes_perfil_admin",
                    "icon": "user-cog",
                },
            ]
        )

    return {"app_nav": nav}
