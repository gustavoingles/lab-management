from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, View

from accounts.models import SolicitacaoAlteracaoPerfil, StatusSolicitacaoPerfil
from accounts.permissions import PERFIS_GESTAO
from accounts.services.solicitacao_perfil import (
    aprovar_solicitacao,
    cancelar_solicitacao,
    criar_solicitacao,
    rejeitar_solicitacao,
)
from accounts.web_forms import SolicitacaoAlteracaoPerfilForm
from lab_management.mixins import PerfilRequiredMixin


class MinhaSolicitacaoPerfilView(LoginRequiredMixin, TemplateView):
    template_name = "app/solicitacao_perfil_minha.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["historico"] = SolicitacaoAlteracaoPerfil.objects.filter(
            solicitante=self.request.user
        ).select_related("perfil_solicitado", "perfil_atual", "revisado_por")[:10]
        ctx["pendente"] = SolicitacaoAlteracaoPerfil.objects.filter(
            solicitante=self.request.user,
            status=StatusSolicitacaoPerfil.PENDENTE,
        ).first()
        return ctx


class SolicitacaoAlteracaoPerfilCreateView(LoginRequiredMixin, CreateView):
    template_name = "app/form.html"
    form_class = SolicitacaoAlteracaoPerfilForm
    success_url = reverse_lazy("app:minha_solicitacao_perfil")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Solicitar troca de perfil"
        ctx["intro_template"] = "app/intros/forms/solicitacao_perfil.html"
        ctx["cancel_url"] = reverse("app:minha_solicitacao_perfil")
        ctx["submit_label"] = "Enviar solicitação"
        return ctx

    def form_valid(self, form):
        try:
            criar_solicitacao(
                usuario=self.request.user,
                perfil_solicitado=form.cleaned_data["perfil_solicitado"],
                justificativa=form.cleaned_data["justificativa"],
            )
        except DjangoValidationError as exc:
            msg = exc.messages[0] if getattr(exc, "messages", None) else str(exc)
            form.add_error(None, msg)
            return self.form_invalid(form)
        messages.success(
            self.request,
            "Solicitação enviada. Aguarde a análise do administrador.",
        )
        return redirect(self.success_url)


class SolicitacaoAlteracaoPerfilAdminListView(PerfilRequiredMixin, ListView):
    perfis_required = tuple(PERFIS_GESTAO)
    model = SolicitacaoAlteracaoPerfil
    template_name = "app/solicitacao_perfil_admin.html"
    context_object_name = "solicitacoes"
    paginate_by = 20

    def get_queryset(self):
        qs = SolicitacaoAlteracaoPerfil.objects.select_related(
            "solicitante",
            "perfil_atual",
            "perfil_solicitado",
            "revisado_por",
        ).order_by("-criada_em")
        if status := self.request.GET.get("status"):
            qs = qs.filter(status=status)
        elif self.request.GET.get("todas") != "1":
            qs = qs.filter(status=StatusSolicitacaoPerfil.PENDENTE)
        return qs


class SolicitacaoAlteracaoPerfilAprovarView(PerfilRequiredMixin, View):
    perfis_required = tuple(PERFIS_GESTAO)

    def post(self, request, pk):
        solicitacao = get_object_or_404(SolicitacaoAlteracaoPerfil, pk=pk)
        try:
            aprovar_solicitacao(
                revisor=request.user,
                solicitacao=solicitacao,
                resposta=request.POST.get("resposta_revisao", ""),
            )
            messages.success(request, "Perfil atualizado e solicitação aprovada.")
        except DjangoValidationError as exc:
            messages.error(request, str(exc))
        return redirect("app:solicitacoes_perfil_admin")


class SolicitacaoAlteracaoPerfilRejeitarView(PerfilRequiredMixin, View):
    perfis_required = tuple(PERFIS_GESTAO)

    def post(self, request, pk):
        solicitacao = get_object_or_404(SolicitacaoAlteracaoPerfil, pk=pk)
        try:
            rejeitar_solicitacao(
                revisor=request.user,
                solicitacao=solicitacao,
                resposta=request.POST.get("resposta_revisao", ""),
            )
            messages.success(request, "Solicitação rejeitada.")
        except DjangoValidationError as exc:
            messages.error(request, str(exc))
        return redirect("app:solicitacoes_perfil_admin")


class SolicitacaoAlteracaoPerfilCancelarView(LoginRequiredMixin, View):
    def post(self, request, pk):
        solicitacao = get_object_or_404(
            SolicitacaoAlteracaoPerfil, pk=pk, solicitante=request.user
        )
        try:
            cancelar_solicitacao(usuario=request.user, solicitacao=solicitacao)
            messages.success(request, "Solicitação cancelada.")
        except DjangoValidationError as exc:
            messages.error(request, str(exc))
        return redirect("app:minha_solicitacao_perfil")
