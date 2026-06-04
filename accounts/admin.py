from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import Perfil, SolicitacaoAlteracaoPerfil, Usuario


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nome", "ativo")
    list_filter = ("ativo",)
    search_fields = ("codigo", "nome")


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    ordering = ("email",)
    list_display = ("email", "nome", "perfil", "is_active", "is_staff")
    list_filter = ("is_active", "is_staff", "perfil")
    search_fields = ("email", "nome", "matricula")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Dados pessoais", {"fields": ("nome", "matricula", "cargo", "perfil")}),
        (
            "Permissões",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Datas", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "nome",
                    "perfil",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )
    filter_horizontal = ("groups", "user_permissions")


@admin.register(SolicitacaoAlteracaoPerfil)
class SolicitacaoAlteracaoPerfilAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "solicitante",
        "perfil_atual",
        "perfil_solicitado",
        "status",
        "criada_em",
    )
    list_filter = ("status",)
    search_fields = ("solicitante__email", "solicitante__nome")
    readonly_fields = ("criada_em", "revisada_em")
