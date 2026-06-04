from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Perfil

User = get_user_model()


class UsuarioGestaoAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        for codigo, nome in [
            ("admin", "Administrador"),
            ("gestor", "Gestor"),
            ("solicitante", "Solicitante"),
            ("almoxarife", "Almoxarife"),
        ]:
            Perfil.objects.get_or_create(
                codigo=codigo, defaults={"nome": nome, "descricao": "", "ativo": True}
            )

    def _user(self, perfil_codigo: str, email: str | None = None):
        email = email or f"{perfil_codigo}@lab.test"
        return User.objects.create_user(
            email=email,
            password="SenhaSegura123!",
            nome=perfil_codigo.title(),
            perfil=Perfil.objects.get(codigo=perfil_codigo),
        )

    def test_gestor_pode_alterar_perfil_para_almoxarife(self):
        gestor = self._user("gestor", "gestor2@lab.test")
        alvo = self._user("solicitante", "alvo@lab.test")
        self.client.force_authenticate(user=gestor)
        perfil_almox = Perfil.objects.get(codigo="almoxarife")
        response = self.client.patch(
            f"/api/v1/auth/usuarios/{alvo.id}/",
            {"perfil_id": perfil_almox.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        alvo.refresh_from_db()
        self.assertEqual(alvo.perfil.codigo, "almoxarife")

    def test_gestor_nao_pode_promover_a_admin(self):
        gestor = self._user("gestor", "gestor3@lab.test")
        alvo = self._user("solicitante", "alvo2@lab.test")
        perfil_admin = Perfil.objects.get(codigo="admin")
        self.client.force_authenticate(user=gestor)
        response = self.client.patch(
            f"/api/v1/auth/usuarios/{alvo.id}/",
            {"perfil_id": perfil_admin.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_pode_promover_a_admin(self):
        admin = self._user("admin", "admin2@lab.test")
        alvo = self._user("gestor", "alvo3@lab.test")
        perfil_admin = Perfil.objects.get(codigo="admin")
        self.client.force_authenticate(user=admin)
        response = self.client.patch(
            f"/api/v1/auth/usuarios/{alvo.id}/",
            {"perfil_id": perfil_admin.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        alvo.refresh_from_db()
        self.assertEqual(alvo.perfil.codigo, "admin")

    def test_solicitante_nao_acessa_lista_usuarios(self):
        sol = self._user("solicitante", "sol2@lab.test")
        self.client.force_authenticate(user=sol)
        response = self.client.get("/api/v1/auth/usuarios/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
