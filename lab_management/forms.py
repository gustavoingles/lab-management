from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from accounts.models import Perfil

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    nome = forms.CharField(label="Nome completo", max_length=200, required=True)
    email = forms.EmailField(label="E-mail", max_length=254, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("nome", "email")

    def clean_email(self):
        email = self.cleaned_data.get("email", "").lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Um usuário com este e-mail já existe.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].lower()
        user.nome = self.cleaned_data["nome"]
        user.perfil = Perfil.objects.get(codigo="solicitante")
        if commit:
            user.save()
        return user
