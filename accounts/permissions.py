from rest_framework import permissions

# Perfis do domínio (seed em accounts.0002_seed_perfis)
PERFIL_ADMIN = "admin"
PERFIL_GESTOR = "gestor"
PERFIL_ALMOXARIFE = "almoxarife"
PERFIL_SOLICITANTE = "solicitante"
PERFIL_TECNICO_LAB = "tecnico_lab"
PERFIL_TECNICO_MANUTENCAO = "tecnico_manutencao"
PERFIL_AUDITOR = "auditor"
PERFIL_FISCAL = "fiscal"

PERFIS_GESTAO = {PERFIL_ADMIN, PERFIL_GESTOR}
PERFIS_ESTOQUE = PERFIS_GESTAO | {PERFIL_ALMOXARIFE}
PERFIS_SOLICITACAO = {PERFIL_SOLICITANTE, PERFIL_TECNICO_LAB}
PERFIS_MANUTENCAO = {PERFIL_TECNICO_MANUTENCAO}
PERFIS_LEITURA_AMPLA = PERFIS_ESTOQUE | PERFIS_SOLICITACAO | PERFIS_MANUTENCAO | {
    PERFIL_AUDITOR,
    PERFIL_FISCAL,
}


def usuario_tem_perfil(user, *codigos: str) -> bool:
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.perfil.codigo in codigos


class PerfilPermission(permissions.BasePermission):
    """Leitura e escrita controladas por conjuntos de perfil."""

    read_perfis: set[str] = PERFIS_LEITURA_AMPLA
    write_perfis: set[str] = PERFIS_GESTAO

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        codigo = user.perfil.codigo
        if request.method in permissions.SAFE_METHODS:
            return codigo in self.read_perfis
        return codigo in self.write_perfis


class CanManageCatalog(PerfilPermission):
    read_perfis = PERFIS_LEITURA_AMPLA
    write_perfis = PERFIS_ESTOQUE


class CanManageStock(PerfilPermission):
    read_perfis = PERFIS_LEITURA_AMPLA
    write_perfis = PERFIS_ESTOQUE


class CanManageRequisicoes(PerfilPermission):
    read_perfis = PERFIS_LEITURA_AMPLA
    write_perfis = PERFIS_ESTOQUE | PERFIS_SOLICITACAO


class CanApproveRequisicoes(permissions.BasePermission):
    def has_permission(self, request, view):
        return usuario_tem_perfil(request.user, *PERFIS_GESTAO)


class CanManageOrdensServico(PerfilPermission):
    read_perfis = PERFIS_LEITURA_AMPLA
    write_perfis = PERFIS_GESTAO | PERFIS_MANUTENCAO


class CanManageInventario(PerfilPermission):
    read_perfis = PERFIS_LEITURA_AMPLA
    write_perfis = PERFIS_ESTOQUE


class CanManageBaixas(PerfilPermission):
    read_perfis = PERFIS_LEITURA_AMPLA
    write_perfis = PERFIS_GESTAO | {PERFIL_ALMOXARIFE}


class CanManageUsers(permissions.BasePermission):
    """Lista e edita usuários (admin e gestor). Atribuir perfil admin só para admin."""

    def has_permission(self, request, view):
        return usuario_tem_perfil(request.user, *PERFIS_GESTAO)


class CanManageReservaEquipamento(PerfilPermission):
    read_perfis = PERFIS_LEITURA_AMPLA
    write_perfis = PERFIS_SOLICITACAO | PERFIS_ESTOQUE


class CanViewAuditoria(PerfilPermission):
    read_perfis = PERFIS_GESTAO | {PERFIL_AUDITOR, PERFIL_FISCAL}
    write_perfis = set()  # auditoria só via serviço interno

    def has_permission(self, request, view):
        if request.method not in permissions.SAFE_METHODS:
            return False
        return super().has_permission(request, view)
