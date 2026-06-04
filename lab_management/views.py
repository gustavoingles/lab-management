from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView, TemplateView

from lab_management.forms import CustomUserCreationForm

User = get_user_model()


class PainelView(LoginRequiredMixin, TemplateView):
    template_name = "painel.html"
    login_url = "login"


class RegisterView(CreateView):
    model = User
    template_name = "register.html"
    form_class = CustomUserCreationForm

    def form_valid(self, form):
        self.object = form.save()
        messages.success(
            self.request,
            "Conta criada com sucesso. Entre com seu e-mail e senha.",
        )
        query = urlencode({"email": self.object.email})
        return redirect(f"{reverse('login')}?{query}")
