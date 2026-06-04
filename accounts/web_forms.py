from django import forms

from accounts.models import Perfil, SolicitacaoAlteracaoPerfil

INPUT_CLASS = (
    "flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm "
    "shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
)
TEXTAREA_CLASS = INPUT_CLASS + " min-h-[100px]"


class SolicitacaoAlteracaoPerfilForm(forms.ModelForm):
    class Meta:
        model = SolicitacaoAlteracaoPerfil
        fields = ("perfil_solicitado", "justificativa")
        widgets = {
            "justificativa": forms.Textarea(
                attrs={
                    "class": TEXTAREA_CLASS,
                    "placeholder": "Explique por que precisa deste perfil no laboratório.",
                }
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user:
            self.fields["perfil_solicitado"].queryset = Perfil.objects.filter(
                ativo=True
            ).exclude(pk=user.perfil_id)
        self.fields["perfil_solicitado"].widget.attrs["class"] = INPUT_CLASS
