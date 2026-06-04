from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Perfil

User = get_user_model()


class AuthAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        Perfil.objects.get_or_create(
            codigo="solicitante",
            defaults={"nome": "Solicitante", "descricao": "", "ativo": True},
        )
        Perfil.objects.get_or_create(
            codigo="admin",
            defaults={"nome": "Administrador", "descricao": "", "ativo": True},
        )

    def _register_payload(self, email="novo@lab.test"):
        return {
            "nome": "Novo Usuário",
            "email": email,
            "password": "SenhaSegura123!",
            "password_confirm": "SenhaSegura123!",
            "matricula": "2026001",
            "cargo": "Estudante",
        }

    def test_register_creates_user_with_default_perfil(self):
        response = self.client.post(
            reverse("api_register"),
            self._register_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="novo@lab.test")
        self.assertEqual(user.nome, "Novo Usuário")
        self.assertEqual(user.perfil.codigo, "solicitante")
        self.assertEqual(user.matricula, "2026001")
        self.assertTrue(user.check_password("SenhaSegura123!"))

    def test_register_rejects_duplicate_email(self):
        self.client.post(
            reverse("api_register"),
            self._register_payload("dup@lab.test"),
            format="json",
        )
        response = self.client.post(
            reverse("api_register"),
            self._register_payload("dup@lab.test"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.filter(email="dup@lab.test").count(), 1)

    def test_register_rejects_password_mismatch(self):
        payload = self._register_payload("mismatch@lab.test")
        payload["password_confirm"] = "OutraSenha123!"
        response = self.client.post(
            reverse("api_register"),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email="mismatch@lab.test").exists())

    def test_token_obtain_pair_with_email(self):
        User.objects.create_user(
            email="login@lab.test",
            password="SenhaSegura123!",
            nome="Login Test",
            perfil=Perfil.objects.get(codigo="solicitante"),
        )
        response = self.client.post(
            reverse("api_token"),
            {"email": "login@lab.test", "password": "SenhaSegura123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_me_requires_authentication(self):
        response = self.client.get(reverse("api_me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_authenticated_user(self):
        user = User.objects.create_user(
            email="me@lab.test",
            password="SenhaSegura123!",
            nome="Eu Mesmo",
            perfil=Perfil.objects.get(codigo="solicitante"),
        )
        self.client.force_authenticate(user=user)
        response = self.client.get(reverse("api_me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "me@lab.test")
        self.assertEqual(response.data["perfil"]["codigo"], "solicitante")
