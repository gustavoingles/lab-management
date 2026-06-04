from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from accounts.permissions import (
    PERFIS_ESTOQUE,
    PERFIS_GESTAO,
    PERFIS_LEITURA_AMPLA,
    PERFIS_MANUTENCAO,
    PERFIS_SOLICITACAO,
    usuario_tem_perfil,
)
from inventory.choices import StatusOrdemServico, StatusRequisicao
from inventory.models import (
    Auditoria,
    Categoria,
    Equipamento,
    Estoque,
    Item,
    Localizacao,
    Movimentacao,
    OrdemServico,
    Requisicao,
    RequisicaoItem,
)
from inventory.services import (
    aprovar_requisicao,
    atender_requisicao_item,
    encerrar_ordem_servico,
    iniciar_ordem_servico,
    rejeitar_requisicao,
    registrar_movimentacao,
)
from lab_management.mixins import PerfilRequiredMixin
from lab_management.web_forms import (
    CategoriaForm,
    EquipamentoForm,
    ItemForm,
    LocalizacaoForm,
    MovimentacaoForm,
    OrdemServicoForm,
    RequisicaoForm,
    RequisicaoItemForm,
    UsuarioPerfilForm,
)

User = get_user_model()


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "app/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_itens"] = Item.objects.filter(ativo=True).count()
        ctx["requisicoes_abertas"] = Requisicao.objects.filter(
            status__in=[StatusRequisicao.ABERTA, StatusRequisicao.EM_APROVACAO]
        ).count()
        ctx["alertas_estoque"] = sum(
            1 for e in Estoque.objects.select_related("item", "localizacao") if e.abaixo_alerta
        )
        ctx["os_abertas"] = OrdemServico.objects.filter(
            status__in=[StatusOrdemServico.ABERTA, StatusOrdemServico.EM_EXECUCAO]
        ).count()
        return ctx


class CategoriaListView(PerfilRequiredMixin, ListView):
    perfis_required = tuple(PERFIS_LEITURA_AMPLA)
    model = Categoria
    template_name = "app/categoria_list.html"
    context_object_name = "categorias"
    paginate_by = 15


class CategoriaCreateView(PerfilRequiredMixin, CreateView):
    perfis_required = tuple(PERFIS_ESTOQUE)
    model = Categoria
    form_class = CategoriaForm
    template_name = "app/form.html"
    success_url = reverse_lazy("app:categorias")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Nova categoria"
        ctx["cancel_url"] = reverse("app:categorias")
        return ctx


class ItemListView(PerfilRequiredMixin, ListView):
    perfis_required = tuple(PERFIS_LEITURA_AMPLA)
    model = Item
    template_name = "app/item_list.html"
    context_object_name = "itens"
    paginate_by = 20

    def get_queryset(self):
        qs = Item.objects.select_related("categoria", "unidade_medida")
        if tipo := self.request.GET.get("tipo"):
            qs = qs.filter(tipo_item=tipo)
        return qs.order_by("nome")


class ItemCreateView(PerfilRequiredMixin, CreateView):
    perfis_required = tuple(PERFIS_ESTOQUE)
    model = Item
    form_class = ItemForm
    template_name = "app/form.html"
    success_url = reverse_lazy("app:itens")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Novo item"
        ctx["cancel_url"] = reverse("app:itens")
        return ctx


class EquipamentoListView(PerfilRequiredMixin, ListView):
    perfis_required = tuple(PERFIS_LEITURA_AMPLA)
    model = Equipamento
    template_name = "app/equipamento_list.html"
    context_object_name = "equipamentos"
    paginate_by = 20

    def get_queryset(self):
        return Equipamento.objects.select_related("item").order_by("-updated_at")


class EquipamentoCreateView(PerfilRequiredMixin, CreateView):
    perfis_required = tuple(PERFIS_ESTOQUE)
    model = Equipamento
    form_class = EquipamentoForm
    template_name = "app/form.html"
    success_url = reverse_lazy("app:equipamentos")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Novo equipamento"
        ctx["cancel_url"] = reverse("app:equipamentos")
        return ctx


class LocalizacaoListView(PerfilRequiredMixin, ListView):
    perfis_required = tuple(PERFIS_LEITURA_AMPLA)
    model = Localizacao
    template_name = "app/localizacao_list.html"
    context_object_name = "localizacoes"
    paginate_by = 20


class LocalizacaoCreateView(PerfilRequiredMixin, CreateView):
    perfis_required = tuple(PERFIS_ESTOQUE)
    model = Localizacao
    form_class = LocalizacaoForm
    template_name = "app/form.html"
    success_url = reverse_lazy("app:localizacoes")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Nova localização"
        ctx["cancel_url"] = reverse("app:localizacoes")
        return ctx


class EstoqueListView(PerfilRequiredMixin, ListView):
    perfis_required = tuple(PERFIS_LEITURA_AMPLA)
    model = Estoque
    template_name = "app/estoque_list.html"
    context_object_name = "estoques"
    paginate_by = 25

    def get_queryset(self):
        return Estoque.objects.select_related("item", "localizacao").order_by(
            "item__nome"
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["alertas"] = [e for e in Estoque.objects.select_related("item") if e.abaixo_alerta]
        return ctx


class MovimentacaoCreateView(PerfilRequiredMixin, FormView):
    perfis_required = tuple(PERFIS_ESTOQUE)
    template_name = "app/form.html"
    form_class = MovimentacaoForm
    success_url = reverse_lazy("app:movimentacoes")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Registrar movimentação"
        ctx["cancel_url"] = reverse("app:estoques")
        return ctx

    def form_valid(self, form):
        data = form.cleaned_data
        try:
            registrar_movimentacao(
                request=self.request,
                item=data["item"],
                tipo_movimentacao=data["tipo_movimentacao"],
                quantidade=data["quantidade"],
                localizacao_origem_id=data["localizacao_origem"].pk
                if data.get("localizacao_origem")
                else None,
                localizacao_destino_id=data["localizacao_destino"].pk
                if data.get("localizacao_destino")
                else None,
                lote=data.get("lote"),
                motivo=data.get("motivo", ""),
            )
        except Exception as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        messages.success(self.request, "Movimentação registrada.")
        return redirect(self.success_url)


class MovimentacaoListView(PerfilRequiredMixin, ListView):
    perfis_required = tuple(PERFIS_LEITURA_AMPLA)
    model = Movimentacao
    template_name = "app/movimentacao_list.html"
    context_object_name = "movimentacoes"
    paginate_by = 25

    def get_queryset(self):
        return Movimentacao.objects.select_related(
            "item", "usuario", "localizacao_origem", "localizacao_destino"
        ).order_by("-created_at")


class RequisicaoListView(PerfilRequiredMixin, ListView):
    perfis_required = tuple(PERFIS_ESTOQUE | PERFIS_SOLICITACAO)
    model = Requisicao
    template_name = "app/requisicao_list.html"
    context_object_name = "requisicoes"
    paginate_by = 15

    def get_queryset(self):
        qs = Requisicao.objects.select_related("solicitante", "aprovador").order_by(
            "-data_solicitacao"
        )
        if not usuario_tem_perfil(self.request.user, *PERFIS_GESTAO) and not self.request.user.is_superuser:
            qs = qs.filter(solicitante=self.request.user)
        return qs


class RequisicaoCreateView(PerfilRequiredMixin, CreateView):
    perfis_required = tuple(PERFIS_ESTOQUE | PERFIS_SOLICITACAO)
    model = Requisicao
    form_class = RequisicaoForm
    template_name = "app/form.html"

    def form_valid(self, form):
        form.instance.solicitante = self.request.user
        messages.success(self.request, "Requisição criada.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("app:requisicao_detalhe", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Nova requisição"
        ctx["cancel_url"] = reverse("app:requisicoes")
        return ctx


class RequisicaoDetailView(PerfilRequiredMixin, DetailView):
    perfis_required = tuple(PERFIS_ESTOQUE | PERFIS_SOLICITACAO)
    model = Requisicao
    template_name = "app/requisicao_detail.html"
    context_object_name = "requisicao"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["item_form"] = RequisicaoItemForm()
        ctx["pode_aprovar"] = usuario_tem_perfil(self.request.user, *PERFIS_GESTAO)
        ctx["pode_atender"] = usuario_tem_perfil(self.request.user, *PERFIS_ESTOQUE)
        ctx["localizacoes"] = Localizacao.objects.filter(ativa=True)
        return ctx


class RequisicaoItemAddView(PerfilRequiredMixin, View):
    perfis_required = tuple(PERFIS_ESTOQUE | PERFIS_SOLICITACAO)

    def post(self, request, pk):
        requisicao = get_object_or_404(Requisicao, pk=pk)
        form = RequisicaoItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.requisicao = requisicao
            item.save()
            messages.success(request, "Item adicionado à requisição.")
        else:
            messages.error(request, "Erro ao adicionar item.")
        return redirect("app:requisicao_detalhe", pk=pk)


class RequisicaoAprovarView(PerfilRequiredMixin, View):
    perfis_required = tuple(PERFIS_GESTAO)

    def post(self, request, pk):
        requisicao = get_object_or_404(Requisicao, pk=pk)
        try:
            aprovar_requisicao(request=request, requisicao=requisicao)
            messages.success(request, "Requisição aprovada.")
        except Exception as exc:
            messages.error(request, str(exc))
        return redirect("app:requisicao_detalhe", pk=pk)


class RequisicaoRejeitarView(PerfilRequiredMixin, View):
    perfis_required = tuple(PERFIS_GESTAO)

    def post(self, request, pk):
        requisicao = get_object_or_404(Requisicao, pk=pk)
        try:
            rejeitar_requisicao(
                request=request,
                requisicao=requisicao,
                motivo=request.POST.get("motivo", ""),
            )
            messages.success(request, "Requisição rejeitada.")
        except Exception as exc:
            messages.error(request, str(exc))
        return redirect("app:requisicao_detalhe", pk=pk)


class RequisicaoAtenderItemView(PerfilRequiredMixin, View):
    perfis_required = tuple(PERFIS_ESTOQUE)

    def post(self, request, pk, item_pk):
        linha = get_object_or_404(RequisicaoItem, pk=item_pk, requisicao_id=pk)
        loc_id = request.POST.get("localizacao_origem_id")
        if not loc_id:
            messages.error(request, "Informe a localização de origem.")
            return redirect("app:requisicao_detalhe", pk=pk)
        try:
            atender_requisicao_item(
                request=request,
                linha=linha,
                localizacao_origem_id=int(loc_id),
                lote_id=int(request.POST["lote_id"])
                if request.POST.get("lote_id")
                else None,
            )
            messages.success(request, "Item atendido.")
        except Exception as exc:
            messages.error(request, str(exc))
        return redirect("app:requisicao_detalhe", pk=pk)


class OrdemServicoListView(PerfilRequiredMixin, ListView):
    perfis_required = tuple(PERFIS_LEITURA_AMPLA)
    model = OrdemServico
    template_name = "app/ordem_servico_list.html"
    context_object_name = "ordens"
    paginate_by = 15


class OrdemServicoCreateView(PerfilRequiredMixin, CreateView):
    perfis_required = tuple(PERFIS_GESTAO | PERFIS_MANUTENCAO)
    model = OrdemServico
    form_class = OrdemServicoForm
    template_name = "app/form.html"
    success_url = reverse_lazy("app:ordens_servico")

    def form_valid(self, form):
        form.instance.solicitante = self.request.user
        messages.success(self.request, "Ordem de serviço aberta.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Nova ordem de serviço"
        ctx["cancel_url"] = reverse("app:ordens_servico")
        return ctx


class OrdemServicoIniciarView(PerfilRequiredMixin, View):
    perfis_required = tuple(PERFIS_GESTAO | PERFIS_MANUTENCAO)

    def post(self, request, pk):
        ordem = get_object_or_404(OrdemServico, pk=pk)
        try:
            iniciar_ordem_servico(request=request, ordem=ordem)
            messages.success(request, "OS em execução.")
        except Exception as exc:
            messages.error(request, str(exc))
        return redirect("app:ordens_servico")


class OrdemServicoEncerrarView(PerfilRequiredMixin, View):
    perfis_required = tuple(PERFIS_GESTAO | PERFIS_MANUTENCAO)

    def post(self, request, pk):
        ordem = get_object_or_404(OrdemServico, pk=pk)
        try:
            encerrar_ordem_servico(request=request, ordem=ordem)
            messages.success(request, "OS encerrada.")
        except Exception as exc:
            messages.error(request, str(exc))
        return redirect("app:ordens_servico")


class AuditoriaListView(PerfilRequiredMixin, ListView):
    perfis_required = tuple(PERFIS_GESTAO | {"auditor", "fiscal"})  # noqa: RUF005
    model = Auditoria
    template_name = "app/auditoria_list.html"
    context_object_name = "auditorias"
    paginate_by = 30

    def get_queryset(self):
        return Auditoria.objects.select_related("usuario").order_by("-created_at")


class UsuarioListView(PerfilRequiredMixin, ListView):
    perfis_required = tuple(PERFIS_GESTAO)
    model = User
    template_name = "app/usuario_list.html"
    context_object_name = "usuarios"
    paginate_by = 20

    def get_queryset(self):
        return User.objects.select_related("perfil").order_by("nome")


class UsuarioUpdateView(PerfilRequiredMixin, UpdateView):
    perfis_required = tuple(PERFIS_GESTAO)
    model = User
    form_class = UsuarioPerfilForm
    template_name = "app/form.html"
    success_url = reverse_lazy("app:usuarios")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["actor"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = f"Editar {self.object.nome}"
        ctx["cancel_url"] = reverse("app:usuarios")
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Usuário atualizado.")
        return super().form_valid(form)
