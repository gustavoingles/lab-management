from django import forms
from django.contrib.auth import get_user_model

from accounts.models import Perfil
from accounts.permissions import PERFIL_ADMIN
from inventory.choices import (
    Prioridade,
    StatusInventario,
    StatusOperacional,
    TipoBaixa,
    TipoManutencao,
    TipoMovimentacao,
)
from inventory.models import (
    Baixa,
    Categoria,
    Equipamento,
    Inventario,
    InventarioItem,
    Item,
    Localizacao,
    Lote,
    Manutencao,
    OrdemServico,
    Requisicao,
    RequisicaoItem,
    ReservaEquipamento,
    UnidadeMedida,
)
from inventory.models import Estoque

User = get_user_model()

INPUT_CLASS = (
    "flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm "
    "shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
)
SELECT_CLASS = INPUT_CLASS
TEXTAREA_CLASS = INPUT_CLASS + " min-h-[80px]"


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.Select):
                widget.attrs.setdefault("class", SELECT_CLASS)
            elif isinstance(widget, forms.Textarea):
                widget.attrs.setdefault("class", TEXTAREA_CLASS)
            elif isinstance(widget, (forms.TextInput, forms.EmailInput, forms.NumberInput, forms.DateInput)):
                widget.attrs.setdefault("class", INPUT_CLASS)
            elif isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "h-4 w-4 rounded border-input")


class CategoriaForm(StyledModelForm):
    class Meta:
        model = Categoria
        fields = ("codigo", "nome", "descricao", "ativa")


class LocalizacaoForm(StyledModelForm):
    class Meta:
        model = Localizacao
        fields = ("nome", "codigo", "tipo", "localizacao_pai", "ativa")


class ItemForm(StyledModelForm):
    class Meta:
        model = Item
        fields = (
            "codigo_interno",
            "nome",
            "descricao",
            "categoria",
            "unidade_medida",
            "tipo_item",
            "controlado",
            "ativo",
        )


class EquipamentoForm(StyledModelForm):
    class Meta:
        model = Equipamento
        fields = (
            "item",
            "numero_serie",
            "tombamento",
            "marca",
            "modelo",
            "status_operacional",
            "data_aquisicao",
        )


class MovimentacaoForm(forms.Form):
    item = forms.ModelChoiceField(queryset=Item.objects.filter(ativo=True))
    tipo_movimentacao = forms.ChoiceField(choices=TipoMovimentacao.choices)
    quantidade = forms.DecimalField(max_digits=14, decimal_places=3, min_value=0.001)
    localizacao_origem = forms.ModelChoiceField(
        queryset=Localizacao.objects.filter(ativa=True),
        required=False,
    )
    localizacao_destino = forms.ModelChoiceField(
        queryset=Localizacao.objects.filter(ativa=True),
        required=False,
    )
    lote = forms.ModelChoiceField(queryset=Lote.objects.all(), required=False)
    motivo = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("class", INPUT_CLASS)
            else:
                field.widget.attrs.setdefault("class", TEXTAREA_CLASS)


class RequisicaoForm(StyledModelForm):
    class Meta:
        model = Requisicao
        fields = ("finalidade", "justificativa", "prioridade", "setor_solicitante")
        widgets = {"prioridade": forms.Select(choices=Prioridade.choices)}


class RequisicaoItemForm(StyledModelForm):
    class Meta:
        model = RequisicaoItem
        fields = ("item", "quantidade_solicitada", "observacao")


class OrdemServicoForm(StyledModelForm):
    class Meta:
        model = OrdemServico
        fields = ("equipamento", "descricao_problema", "prioridade")
        widgets = {"prioridade": forms.Select(choices=Prioridade.choices)}


class UnidadeMedidaForm(StyledModelForm):
    class Meta:
        model = UnidadeMedida
        fields = ("nome", "sigla", "permite_fracionamento")


class LoteForm(StyledModelForm):
    class Meta:
        model = Lote
        fields = (
            "item",
            "codigo_lote",
            "fabricante",
            "data_fabricacao",
            "data_validade",
            "quantidade_disponivel",
        )
        widgets = {
            "data_fabricacao": forms.DateInput(attrs={"type": "date"}),
            "data_validade": forms.DateInput(attrs={"type": "date"}),
        }


class EstoqueNiveisForm(StyledModelForm):
    class Meta:
        model = Estoque
        fields = ("nivel_minimo", "nivel_alerta")


class ManutencaoForm(StyledModelForm):
    class Meta:
        model = Manutencao
        fields = (
            "ordem_servico",
            "tipo_manutencao",
            "descricao",
            "resultado",
            "realizada_em",
            "custo_estimado",
            "proximo_vencimento",
        )
        widgets = {
            "tipo_manutencao": forms.Select(choices=TipoManutencao.choices),
            "realizada_em": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "proximo_vencimento": forms.DateInput(attrs={"type": "date"}),
            "descricao": forms.Textarea(attrs={"rows": 3}),
            "resultado": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, ordem_servico=None, **kwargs):
        super().__init__(*args, **kwargs)
        if ordem_servico is not None:
            self.fields["ordem_servico"].initial = ordem_servico
            self.fields["ordem_servico"].queryset = OrdemServico.objects.filter(
                pk=ordem_servico.pk
            )


class InventarioForm(StyledModelForm):
    class Meta:
        model = Inventario
        fields = ("nome", "descricao", "status", "responsavel")
        widgets = {"status": forms.Select(choices=StatusInventario.choices)}


class InventarioItemForm(StyledModelForm):
    class Meta:
        model = InventarioItem
        fields = (
            "item",
            "localizacao",
            "quantidade_sistema",
            "quantidade_contada",
            "observacao",
        )
        widgets = {"observacao": forms.Textarea(attrs={"rows": 2})}


class ReservaEquipamentoForm(StyledModelForm):
    class Meta:
        model = ReservaEquipamento
        fields = ("equipamento", "finalidade", "inicio", "fim", "observacao")
        widgets = {
            "inicio": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "fim": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "finalidade": forms.Textarea(attrs={"rows": 3}),
            "observacao": forms.Textarea(attrs={"rows": 2}),
        }


class BaixaForm(StyledModelForm):
    class Meta:
        model = Baixa
        fields = (
            "item",
            "equipamento",
            "tipo_baixa",
            "motivo",
            "destino_final",
            "documento_referencia",
        )
        widgets = {
            "tipo_baixa": forms.Select(choices=TipoBaixa.choices),
            "motivo": forms.Textarea(attrs={"rows": 3}),
            "destino_final": forms.Textarea(attrs={"rows": 2}),
        }

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("item") and not cleaned.get("equipamento"):
            raise forms.ValidationError("Informe um item ou um equipamento.")
        return cleaned


class UsuarioPerfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("nome", "cargo", "matricula", "perfil", "is_active")

    def __init__(self, *args, actor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.actor = actor
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", SELECT_CLASS)
            else:
                field.widget.attrs.setdefault("class", INPUT_CLASS)

    def clean_perfil(self):
        perfil = self.cleaned_data["perfil"]
        actor = self.actor
        if not actor or actor.is_superuser:
            return perfil
        if perfil.codigo == PERFIL_ADMIN and actor.perfil.codigo != PERFIL_ADMIN:
            raise forms.ValidationError("Apenas admin pode atribuir perfil admin.")
        if (
            self.instance
            and self.instance.perfil.codigo == PERFIL_ADMIN
            and actor.perfil.codigo != PERFIL_ADMIN
        ):
            raise forms.ValidationError("Apenas admin pode alterar usuários admin.")
        return perfil
