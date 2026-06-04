from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Perfil

User = get_user_model()


class PerfilPermissionTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        for codigo, nome in [
            ("solicitante", "Solicitante"),
            ("admin", "Administrador"),
            ("almoxarife", "Almoxarife"),
        ]:
            Perfil.objects.get_or_create(
                codigo=codigo, defaults={"nome": nome, "descricao": "", "ativo": True}
            )

    def _user(self, perfil_codigo: str):
        return User.objects.create_user(
            email=f"{perfil_codigo}@lab.test",
            password="SenhaSegura123!",
            nome=perfil_codigo.title(),
            perfil=Perfil.objects.get(codigo=perfil_codigo),
        )

    def test_solicitante_cannot_create_categoria(self):
        self.client.force_authenticate(user=self._user("solicitante"))
        response = self.client.post(
            "/api/v1/categorias/",
            {"codigo": "CAT-X", "nome": "Categoria X", "ativa": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_almoxarife_can_create_categoria(self):
        self.client.force_authenticate(user=self._user("almoxarife"))
        response = self.client.post(
            "/api/v1/categorias/",
            {"codigo": "CAT-Y", "nome": "Categoria Y", "ativa": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
