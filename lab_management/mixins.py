from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.deletion import ProtectedError, RestrictedError
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DeleteView

from accounts.permissions import PERFIS_ESTOQUE, usuario_tem_perfil

_TIPO_VINCULO_LABEL = {
    "Movimentacao": "movimentação de estoque",
    "RequisicaoItem": "linha de requisição",
    "InventarioItem": "linha de inventário",
    "Baixa": "baixa/descarte",
    "Estoque": "saldo em estoque",
    "Lote": "lote",
    "Equipamento": "equipamento",
    "Item": "item",
    "UnidadeMedida": "item",
    "Categoria": "item",
}


def _descrever_objeto_vinculado(obj) -> str:
    texto = str(obj)
    if texto.startswith(f"{obj.__class__.__name__} object ("):
        rotulo = _TIPO_VINCULO_LABEL.get(
            obj.__class__.__name__,
            obj._meta.verbose_name,
        )
        return f"{rotulo} #{obj.pk}"
    return texto


class PerfilRequiredMixin(LoginRequiredMixin):
    """Restringe a view aos perfis listados (superusuário sempre passa)."""

    perfis_required: tuple[str, ...] = ()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.is_superuser:
            return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)
        if self.perfis_required and not usuario_tem_perfil(
            request.user, *self.perfis_required
        ):
            messages.error(
                request,
                "Seu perfil não tem permissão para acessar esta página.",
            )
            return redirect("app:dashboard")
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class FormPageMixin:
    page_title = ""
    cancel_url_name = ""
    intro_template = ""

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.setdefault("page_title", self.page_title)
        if self.cancel_url_name:
            ctx.setdefault("cancel_url", reverse(self.cancel_url_name))
        if self.intro_template:
            ctx.setdefault("intro_template", self.intro_template)
        return ctx


class PodeEscreverMixin:
    """Injeta flags de escrita nas listagens conforme o perfil."""

    write_perfis: tuple[str, ...] = tuple(PERFIS_ESTOQUE)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["pode_escrever"] = user.is_superuser or usuario_tem_perfil(
            user, *self.write_perfis
        )
        return ctx


class ConfirmDeleteView(PerfilRequiredMixin, DeleteView):
    template_name = "app/confirm_delete.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Confirmar exclusão"
        ctx["cancel_url"] = self.success_url
        ctx["intro_template"] = "app/intros/confirm_delete.html"
        return ctx

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except (ProtectedError, RestrictedError) as exc:
            vinculados = getattr(exc, "protected_objects", None) or getattr(
                exc, "restricted_objects", None
            )
            if vinculados:
                lista = list(vinculados)
                exemplos = ", ".join(
                    _descrever_objeto_vinculado(obj) for obj in lista[:3]
                )
                sufixo = f" Ex.: {exemplos}." if exemplos else ""
                if len(lista) > 3:
                    sufixo += f" (+{len(lista) - 3} outros)"
            else:
                sufixo = ""
            messages.error(
                self.request,
                "Não é possível excluir: existem registros vinculados no sistema."
                + sufixo,
            )
            return redirect(self.success_url)
        messages.success(self.request, "Registro excluído.")
        return response
