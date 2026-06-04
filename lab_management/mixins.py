from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

from accounts.permissions import usuario_tem_perfil


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
