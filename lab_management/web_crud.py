"""Views CRUD adicionais do painel /app/ (edição, exclusão e módulos da API)."""

import csv

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from accounts.permissions import (
    PERFIS_ESTOQUE,
    PERFIS_GESTAO,
    PERFIS_LEITURA_AMPLA,
    PERFIS_MANUTENCAO,
    PERFIS_SOLICITACAO,
    PERFIL_ALMOXARIFE,
    usuario_tem_perfil,
)
from inventory.models import (
    Auditoria,
    Baixa,
    Categoria,
    Equipamento,
    Estoque,
    Inventario,
    InventarioItem,
    Item,
    Localizacao,
    Lote,
    Manutencao,
    Movimentacao,
    OrdemServico,
    ReservaEquipamento,
    UnidadeMedida,
)
from inventory.services.laudos import gerar_laudo_os
from inventory.services.reservas_equipamento import (
    aprovar_reserva_equipamento,
    cancelar_reserva_equipamento,
    criar_reserva_equipamento,
    encerrar_reserva_equipamento,
)
from lab_management.mixins import (
    ConfirmDeleteView,
    FormPageMixin,
    PerfilRequiredMixin,
    PodeEscreverMixin,
)
from lab_management.web_forms import (
    BaixaForm,
    CategoriaForm,
    ReservaEquipamentoForm,
    EquipamentoForm,
    EstoqueNiveisForm,
    InventarioForm,
    InventarioItemForm,
    ItemForm,
    LocalizacaoForm,
    LoteForm,
    ManutencaoForm,
    UnidadeMedidaForm,
)

PERFIS_BAIXA = tuple(PERFIS_GESTAO | {PERFIL_ALMOXARIFE})
PERFIS_OS_WRITE = tuple(PERFIS_GESTAO | PERFIS_MANUTENCAO)


# --- Categoria ---


class CategoriaUpdateView(PerfilRequiredMixin, FormPageMixin, UpdateView):
    perfis_required = tuple(PERFIS_ESTOQUE)
    model = Categoria
    form_class = CategoriaForm
    template_name = "app/form.html"
    page_title = "Editar categoria"
    intro_template = "app/intros/forms/categoria.html"
    cancel_url_name = "app:categorias"
    success_url = reverse_lazy("app:categorias")

    def form_valid(self, form):
        messages.success(self.request, "Categoria atualizada.")
        return super().form_valid(form)


class CategoriaDeleteView(ConfirmDeleteView):
    perfis_required = tuple(PERFIS_ESTOQUE)
    model = Categoria
    success_url = reverse_lazy("app:categorias")


# --- Unidade de medida ---


class UnidadeMedidaListView(PerfilRequiredMixin, PodeEscreverMixin, ListView):
    perfis_required = tuple(PERFIS_LEITURA_AMPLA)
    model = UnidadeMedida
    template_name = "app/unidade_medida_list.html"
    context_object_name = "unidades"
    paginate_by = 20


class UnidadeMedidaCreateView(PerfilRequiredMixin, FormPageMixin, CreateView):
    perfis_required = tuple(PERFIS_ESTOQUE)
    model = UnidadeMedida
    form_class = UnidadeMedidaForm
    template_name = "app/form.html"
    page_title = "Nova unidade de medida"
    intro_template = "app/intros/forms/unidade_medida.html"
    cancel_url_name = "app:unidades_medida"
    success_url = reverse_lazy("app:unidades_medida")

    def form_valid(self, form):
        messages.success(self.request, "Unidade de medida criada.")
        return super().form_valid(form)


class UnidadeMedidaUpdateView(PerfilRequiredMixin, FormPageMixin, UpdateView):
    perfis_required = tuple(PERFIS_ESTOQUE)
    model = UnidadeMedida
    form_class = UnidadeMedidaForm
    template_name = "app/form.html"
    page_title = "Editar unidade de medida"
    intro_template = "app/intros/forms/unidade_medida.html"
    cancel_url_name = "app:unidades_medida"
    success_url = reverse_lazy("app:unidades_medida")

    def form_valid(self, form):
        messages.success(self.request, "Unidade de medida atualizada.")
        return super().form_valid(form)


class UnidadeMedidaDeleteView(ConfirmDeleteView):
    perfis_required = tuple(PERFIS_ESTOQUE)
    model = UnidadeMedida
    success_url = reverse_lazy("app:unidades_medida")


# --- Localização ---


class LocalizacaoUpdateView(PerfilRequiredMixin, FormPageMixin, UpdateView):
    perfis_required = tuple(PERFIS_ESTOQUE)
    model = Localizacao
    form_class = LocalizacaoForm
    template_name = "app/form.html"
    page_title = "Editar localização"
    intro_template = "app/intros/forms/localizacao.html"
    cancel_url_name = "app:localizacoes"
    success_url = reverse_lazy("app:localizacoes")

    def form_valid(self, form):
        messages.success(self.request, "Localização atualizada.")
        return super().form_valid(form)


class LocalizacaoDeleteView(ConfirmDeleteView):
    perfis_required = tuple(PERFIS_ESTOQUE)
    model = Localizacao
    success_url = reverse_lazy("app:localizacoes")


# --- Item ---


class ItemUpdateView(PerfilRequiredMixin, FormPageMixin, UpdateView):
    perfis_required = tuple(PERFIS_ESTOQUE)
    model = Item
    form_class = ItemForm
    template_name = "app/form.html"
    page_title = "Editar item"
    intro_template = "app/intros/forms/item.html"
    cancel_url_name = "app:itens"
    success_url = reverse_lazy("app:itens")

    def form_valid(self, form):
        messages.success(self.request, "Item atualizado.")
        return super().form_valid(form)


class ItemDeleteView(ConfirmDeleteView):
    perfis_required = tuple(PERFIS_ESTOQUE)
    model = Item
    success_url = reverse_lazy("app:itens")


# --- Equipamento ---


class EquipamentoUpdateView(PerfilRequiredMixin, FormPageMixin, UpdateView):
    perfis_required = tuple(PERFIS_ESTOQUE)
    model = Equipamento
    form_class = EquipamentoForm
    template_name = "app/form.html"
    page_title = "Editar equipamento"
    intro_template = "app/intros/forms/equipamento.html"
    cancel_url_name = "app:equipamentos"
    success_url = reverse_lazy("app:equipamentos")

    def form_valid(self, form):
        messages.success(self.request, "Equipamento atualizado.")
        return super().form_valid(form)


class EquipamentoDeleteView(ConfirmDeleteView):
    perfis_required = tuple(PERFIS_ESTOQUE)
    model = Equipamento
    success_url = reverse_lazy("app:equipamentos")


# --- Lote ---


class LoteListView(PerfilRequiredMixin, PodeEscreverMixin, ListView):
    perfis_required = tuple(PERFIS_LEITURA_AMPLA)
    model = Lote
    template_name = "app/lote_list.html"
    context_object_name = "lotes"
    paginate_by = 25

    def get_queryset(self):
        qs = Lote.objects.select_related("item").order_by("data_validade", "codigo_lote")
        if item_id := self.request.GET.get("item"):
            qs = qs.filter(item_id=item_id)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["itens"] = Item.objects.filter(ativo=True).order_by("nome")
        ctx["item_filtro"] = self.request.GET.get("item", "")
        return ctx


class LoteCreateView(PerfilRequiredMixin, FormPageMixin, CreateView):
    perfis_required = tuple(PERFIS_ESTOQUE)
    model = Lote
    form_class = LoteForm
    template_name = "app/form.html"
    page_title = "Novo lote"
    intro_template = "app/intros/forms/lote.html"
    cancel_url_name = "app:lotes"
    success_url = reverse_lazy("app:lotes")

    def get_initial(self):
        initial = super().get_initial()
        if item_id := self.request.GET.get("item"):
            initial["item"] = item_id
        return initial

    def form_valid(self, form):
        messages.success(self.request, "Lote cadastrado.")
        return super().form_valid(form)


class LoteUpdateView(PerfilRequiredMixin, FormPageMixin, UpdateView):
    perfis_required = tuple(PERFIS_ESTOQUE)
    model = Lote
    form_class = LoteForm
    template_name = "app/form.html"
    page_title = "Editar lote"
    intro_template = "app/intros/forms/lote.html"
    cancel_url_name = "app:lotes"
    success_url = reverse_lazy("app:lotes")

    def form_valid(self, form):
        messages.success(self.request, "Lote atualizado.")
        return super().form_valid(form)


class LoteDeleteView(ConfirmDeleteView):
    perfis_required = tuple(PERFIS_ESTOQUE)
    model = Lote
    success_url = reverse_lazy("app:lotes")


# --- Estoque (níveis) ---


class EstoqueUpdateView(PerfilRequiredMixin, FormPageMixin, UpdateView):
    perfis_required = tuple(PERFIS_ESTOQUE)
    model = Estoque
    form_class = EstoqueNiveisForm
    template_name = "app/form.html"
    page_title = "Níveis de estoque"
    intro_template = "app/intros/forms/estoque.html"
    cancel_url_name = "app:estoques"
    success_url = reverse_lazy("app:estoques")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = (
            f"Níveis — {self.object.item.nome} em {self.object.localizacao.nome}"
        )
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Níveis de alerta atualizados.")
        return super().form_valid(form)


# --- Ordem de serviço (detalhe + manutenções) ---


class OrdemServicoDetailView(PerfilRequiredMixin, DetailView):
    perfis_required = tuple(PERFIS_LEITURA_AMPLA)
    model = OrdemServico
    template_name = "app/ordem_servico_detail.html"
    context_object_name = "ordem"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["manutencoes"] = self.object.manutencoes.all()
        ctx["pode_manutencao"] = usuario_tem_perfil(
            self.request.user, *PERFIS_OS_WRITE
        )
        return ctx


# --- Manutenção ---


class ManutencaoListView(PerfilRequiredMixin, PodeEscreverMixin, ListView):
    perfis_required = tuple(PERFIS_LEITURA_AMPLA)
    write_perfis = PERFIS_OS_WRITE
    model = Manutencao
    template_name = "app/manutencao_list.html"
    context_object_name = "manutencoes"
    paginate_by = 20

    def get_queryset(self):
        qs = Manutencao.objects.select_related(
            "ordem_servico", "ordem_servico__equipamento"
        ).order_by("-realizada_em", "-id")
        if os_id := self.request.GET.get("os"):
            qs = qs.filter(ordem_servico_id=os_id)
        return qs


class ManutencaoCreateView(PerfilRequiredMixin, FormPageMixin, CreateView):
    perfis_required = PERFIS_OS_WRITE
    model = Manutencao
    form_class = ManutencaoForm
    template_name = "app/form.html"
    page_title = "Registrar manutenção"
    intro_template = "app/intros/forms/manutencao.html"
    cancel_url_name = "app:manutencoes"
    success_url = reverse_lazy("app:manutencoes")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        os_id = self.kwargs.get("os_pk") or self.request.GET.get("os")
        if os_id:
            kwargs["ordem_servico"] = get_object_or_404(OrdemServico, pk=os_id)
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.kwargs.get("os_pk"):
            ctx["cancel_url"] = reverse(
                "app:ordem_servico_detalhe", kwargs={"pk": self.kwargs["os_pk"]}
            )
        return ctx

    def get_success_url(self):
        if self.kwargs.get("os_pk"):
            return reverse(
                "app:ordem_servico_detalhe", kwargs={"pk": self.kwargs["os_pk"]}
            )
        return reverse("app:manutencoes")

    def form_valid(self, form):
        messages.success(self.request, "Manutenção registrada.")
        return super().form_valid(form)


class ManutencaoUpdateView(PerfilRequiredMixin, FormPageMixin, UpdateView):
    perfis_required = PERFIS_OS_WRITE
    model = Manutencao
    form_class = ManutencaoForm
    template_name = "app/form.html"
    page_title = "Editar manutenção"
    intro_template = "app/intros/forms/manutencao.html"
    cancel_url_name = "app:manutencoes"
    success_url = reverse_lazy("app:manutencoes")

    def form_valid(self, form):
        messages.success(self.request, "Manutenção atualizada.")
        return super().form_valid(form)


class ManutencaoDeleteView(ConfirmDeleteView):
    perfis_required = PERFIS_OS_WRITE
    model = Manutencao
    success_url = reverse_lazy("app:manutencoes")


# --- Inventário ---


class InventarioListView(PerfilRequiredMixin, PodeEscreverMixin, ListView):
    perfis_required = tuple(PERFIS_LEITURA_AMPLA)
    model = Inventario
    template_name = "app/inventario_list.html"
    context_object_name = "inventarios"
    paginate_by = 15

    def get_queryset(self):
        return Inventario.objects.select_related("responsavel").order_by("-iniciado_em")


class InventarioCreateView(PerfilRequiredMixin, FormPageMixin, CreateView):
    perfis_required = tuple(PERFIS_ESTOQUE)
    model = Inventario
    form_class = InventarioForm
    template_name = "app/form.html"
    page_title = "Novo inventário"
    intro_template = "app/intros/forms/inventario.html"
    cancel_url_name = "app:inventarios"
    success_url = reverse_lazy("app:inventarios")

    def form_valid(self, form):
        if not form.instance.responsavel_id:
            form.instance.responsavel = self.request.user
        messages.success(self.request, "Inventário criado.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("app:inventario_detalhe", kwargs={"pk": self.object.pk})


class InventarioUpdateView(PerfilRequiredMixin, FormPageMixin, UpdateView):
    perfis_required = tuple(PERFIS_ESTOQUE)
    model = Inventario
    form_class = InventarioForm
    template_name = "app/form.html"
    page_title = "Editar inventário"
    intro_template = "app/intros/forms/inventario.html"
    cancel_url_name = "app:inventarios"
    success_url = reverse_lazy("app:inventarios")

    def form_valid(self, form):
        messages.success(self.request, "Inventário atualizado.")
        return super().form_valid(form)


class InventarioDeleteView(ConfirmDeleteView):
    perfis_required = tuple(PERFIS_ESTOQUE)
    model = Inventario
    success_url = reverse_lazy("app:inventarios")


class InventarioDetailView(PerfilRequiredMixin, DetailView):
    perfis_required = tuple(PERFIS_LEITURA_AMPLA)
    model = Inventario
    template_name = "app/inventario_detail.html"
    context_object_name = "inventario"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["linhas"] = self.object.itens.select_related("item", "localizacao")
        ctx["item_form"] = InventarioItemForm()
        ctx["pode_escrever"] = usuario_tem_perfil(self.request.user, *PERFIS_ESTOQUE)
        return ctx


class InventarioItemAddView(PerfilRequiredMixin, View):
    perfis_required = tuple(PERFIS_ESTOQUE)

    def post(self, request, pk):
        inventario = get_object_or_404(Inventario, pk=pk)
        form = InventarioItemForm(request.POST)
        if form.is_valid():
            linha = form.save(commit=False)
            linha.inventario = inventario
            linha.save()
            messages.success(request, "Linha adicionada ao inventário.")
        else:
            messages.error(request, "Erro ao adicionar linha.")
        return redirect("app:inventario_detalhe", pk=pk)


class InventarioItemDeleteView(ConfirmDeleteView):
    perfis_required = tuple(PERFIS_ESTOQUE)
    model = InventarioItem
    template_name = "app/confirm_delete.html"

    def get_success_url(self):
        return reverse("app:inventario_detalhe", kwargs={"pk": self.object.inventario_id})


# --- Baixa ---


class BaixaListView(PerfilRequiredMixin, PodeEscreverMixin, ListView):
    perfis_required = tuple(PERFIS_LEITURA_AMPLA)
    write_perfis = PERFIS_BAIXA
    model = Baixa
    template_name = "app/baixa_list.html"
    context_object_name = "baixas"
    paginate_by = 20

    def get_queryset(self):
        return Baixa.objects.select_related("item", "equipamento", "usuario").order_by(
            "-realizada_em"
        )


class BaixaCreateView(PerfilRequiredMixin, FormPageMixin, CreateView):
    perfis_required = PERFIS_BAIXA
    model = Baixa
    form_class = BaixaForm
    template_name = "app/form.html"
    page_title = "Registrar baixa / descarte"
    intro_template = "app/intros/forms/baixa.html"
    cancel_url_name = "app:baixas"
    success_url = reverse_lazy("app:baixas")

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, "Baixa registrada.")
        return super().form_valid(form)


class BaixaUpdateView(PerfilRequiredMixin, FormPageMixin, UpdateView):
    perfis_required = PERFIS_BAIXA
    model = Baixa
    form_class = BaixaForm
    template_name = "app/form.html"
    page_title = "Editar baixa"
    intro_template = "app/intros/forms/baixa.html"
    cancel_url_name = "app:baixas"
    success_url = reverse_lazy("app:baixas")

    def form_valid(self, form):
        messages.success(self.request, "Baixa atualizada.")
        return super().form_valid(form)


class BaixaDeleteView(ConfirmDeleteView):
    perfis_required = PERFIS_BAIXA
    model = Baixa
    success_url = reverse_lazy("app:baixas")


# --- Reserva de equipamento ---

PERFIS_RESERVA_EQUIP = tuple(PERFIS_SOLICITACAO | PERFIS_ESTOQUE)


class ReservaEquipamentoListView(PerfilRequiredMixin, PodeEscreverMixin, ListView):
    perfis_required = PERFIS_RESERVA_EQUIP
    model = ReservaEquipamento
    template_name = "app/reserva_equipamento_list.html"
    context_object_name = "reservas"
    paginate_by = 20

    def get_queryset(self):
        qs = ReservaEquipamento.objects.select_related(
            "equipamento", "solicitante"
        ).order_by("-inicio")
        if not usuario_tem_perfil(self.request.user, *PERFIS_GESTAO):
            qs = qs.filter(solicitante=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["pode_aprovar"] = usuario_tem_perfil(self.request.user, *PERFIS_GESTAO)
        ctx["total_equipamentos"] = Equipamento.objects.count()
        return ctx


class ReservaEquipamentoCreateView(PerfilRequiredMixin, PodeEscreverMixin, FormPageMixin, CreateView):
    perfis_required = PERFIS_RESERVA_EQUIP
    model = ReservaEquipamento
    form_class = ReservaEquipamentoForm
    template_name = "app/form.html"
    page_title = "Reservar equipamento"
    intro_template = "app/intros/forms/reserva_equipamento.html"
    cancel_url_name = "app:reservas_equipamento"
    success_url = reverse_lazy("app:reservas_equipamento")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["sem_equipamentos_cadastrados"] = not Equipamento.objects.exists()
        return ctx

    def form_valid(self, form):
        try:
            criar_reserva_equipamento(
                solicitante=self.request.user,
                equipamento_id=form.cleaned_data["equipamento"].pk,
                finalidade=form.cleaned_data["finalidade"],
                inicio=form.cleaned_data["inicio"],
                fim=form.cleaned_data["fim"],
                observacao=form.cleaned_data.get("observacao", ""),
            )
        except Exception as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        messages.success(
            self.request,
            "Reserva solicitada. Aguarde confirmação do gestor.",
        )
        return redirect(self.success_url)


class ReservaEquipamentoAprovarView(PerfilRequiredMixin, View):
    perfis_required = tuple(PERFIS_GESTAO)

    def post(self, request, pk):
        reserva = get_object_or_404(ReservaEquipamento, pk=pk)
        try:
            aprovar_reserva_equipamento(revisor=request.user, reserva=reserva)
            messages.success(request, "Reserva confirmada.")
        except Exception as exc:
            messages.error(request, str(exc))
        return redirect("app:reservas_equipamento")


class ReservaEquipamentoCancelarView(PerfilRequiredMixin, View):
    perfis_required = PERFIS_RESERVA_EQUIP

    def post(self, request, pk):
        reserva = get_object_or_404(ReservaEquipamento, pk=pk)
        try:
            cancelar_reserva_equipamento(usuario=request.user, reserva=reserva)
            messages.success(request, "Reserva cancelada.")
        except Exception as exc:
            messages.error(request, str(exc))
        return redirect("app:reservas_equipamento")


class ReservaEquipamentoEncerrarView(PerfilRequiredMixin, View):
    perfis_required = tuple(PERFIS_GESTAO)

    def post(self, request, pk):
        reserva = get_object_or_404(ReservaEquipamento, pk=pk)
        try:
            encerrar_reserva_equipamento(reserva=reserva)
            messages.success(request, "Reserva encerrada.")
        except Exception as exc:
            messages.error(request, str(exc))
        return redirect("app:reservas_equipamento")


# --- Laudo PDF ---


class OrdemServicoLaudoView(PerfilRequiredMixin, DetailView):
    perfis_required = tuple(PERFIS_LEITURA_AMPLA)
    model = OrdemServico

    def get(self, request, *args, **kwargs):
        ordem = self.get_object()
        pdf_bytes = gerar_laudo_os(ordem)
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="laudo-os-{ordem.pk}.pdf"'
        )
        if not ordem.laudo_emitido:
            OrdemServico.objects.filter(pk=ordem.pk).update(laudo_emitido=True)
        return response


# --- Exportações CSV ---


class InventarioCSVView(PerfilRequiredMixin, DetailView):
    perfis_required = tuple(PERFIS_LEITURA_AMPLA)
    model = Inventario

    def get(self, request, *args, **kwargs):
        inv = self.get_object()
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="inventario-{inv.pk}.csv"'
        )
        response.write("﻿")  # BOM for Excel
        writer = csv.writer(response)
        writer.writerow([
            "Item", "Código interno", "Localização",
            "Qtd sistema", "Qtd contada", "Diferença", "Observação",
        ])
        for linha in inv.itens.select_related("item", "localizacao"):
            writer.writerow([
                linha.item.nome,
                linha.item.codigo_interno,
                linha.localizacao.nome if linha.localizacao else "",
                linha.quantidade_sistema,
                linha.quantidade_contada,
                linha.diferenca,
                linha.observacao,
            ])
        return response


class AuditoriaCSVView(PerfilRequiredMixin, ListView):
    perfis_required = tuple(PERFIS_GESTAO)
    model = Auditoria

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="auditoria.csv"'
        response.write("﻿")
        writer = csv.writer(response)
        writer.writerow(["Data", "Usuário", "Ação", "Entidade", "Entidade ID", "IP"])
        qs = Auditoria.objects.select_related("usuario").order_by("-created_at")
        for a in qs:
            writer.writerow([
                a.created_at.strftime("%d/%m/%Y %H:%M"),
                a.usuario.nome if a.usuario else "",
                a.acao,
                a.entidade,
                a.entidade_id or "",
                a.ip_origem or "",
            ])
        return response


class MovimentacaoCSVView(PerfilRequiredMixin, ListView):
    perfis_required = tuple(PERFIS_LEITURA_AMPLA)
    model = Movimentacao

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="movimentacoes.csv"'
        response.write("﻿")
        writer = csv.writer(response)
        writer.writerow([
            "Data", "Item", "Código interno", "Tipo",
            "Quantidade", "Saldo resultante",
            "Origem", "Destino", "Usuário", "Motivo",
        ])
        qs = Movimentacao.objects.select_related(
            "item", "usuario", "localizacao_origem", "localizacao_destino"
        ).order_by("-created_at")
        for m in qs:
            writer.writerow([
                m.created_at.strftime("%d/%m/%Y %H:%M"),
                m.item.nome,
                m.item.codigo_interno,
                m.get_tipo_movimentacao_display(),
                m.quantidade,
                m.saldo_resultante if m.saldo_resultante is not None else "",
                m.localizacao_origem.nome if m.localizacao_origem else "",
                m.localizacao_destino.nome if m.localizacao_destino else "",
                m.usuario.nome if m.usuario else "",
                m.motivo,
            ])
        return response
