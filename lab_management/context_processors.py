from accounts.permissions import (
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
        nav.append({"label": "Catálogo", "url_name": "app:itens", "icon": "boxes"})

    if usuario_tem_perfil(user, *PERFIS_ESTOQUE):
        nav.extend(
            [
                {"label": "Estoque", "url_name": "app:estoques", "icon": "warehouse"},
                {
                    "label": "Movimentações",
                    "url_name": "app:movimentacao_nova",
                    "icon": "arrow-left-right",
                },
            ]
        )

    if usuario_tem_perfil(user, *PERFIS_ESTOQUE, *PERFIS_SOLICITACAO):
        nav.append(
            {"label": "Requisições", "url_name": "app:requisicoes", "icon": "clipboard-list"}
        )

    if usuario_tem_perfil(user, *PERFIS_GESTAO, *PERFIS_MANUTENCAO):
        nav.append(
            {
                "label": "Ordens de serviço",
                "url_name": "app:ordens_servico",
                "icon": "wrench",
            }
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
