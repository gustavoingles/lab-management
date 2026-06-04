from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DeleteView

from accounts.permissions import PERFIS_ESTOQUE, usuario_tem_perfil


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

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.setdefault("page_title", self.page_title)
        if self.cancel_url_name:
            ctx.setdefault("cancel_url", reverse(self.cancel_url_name))
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
        return ctx

    def form_valid(self, form):
        try:
            messages.success(self.request, "Registro excluído.")
            return super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                "Não é possível excluir: existem registros vinculados.",
            )
            return redirect(self.success_url)
