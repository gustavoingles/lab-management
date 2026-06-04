from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Perfil, SolicitacaoAlteracaoPerfil, StatusSolicitacaoPerfil

User = get_user_model()


class SolicitacaoPerfilAPITestCase(APITestCase):
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
        email = email or f"{perfil_codigo}-sol@lab.test"
        return User.objects.create_user(
            email=email,
            password="SenhaSegura123!",
            nome=perfil_codigo.title(),
            perfil=Perfil.objects.get(codigo=perfil_codigo),
        )

    def test_solicitante_cria_solicitacao_para_almoxarife(self):
        sol = self._user("solicitante", "sol-perfil@lab.test")
        almox = Perfil.objects.get(codigo="almoxarife")
        self.client.force_authenticate(user=sol)
        response = self.client.post(
            "/api/v1/auth/solicitacoes-perfil/",
            {"perfil_id": almox.id, "justificativa": "Trabalho no almoxarifado do lab."},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            SolicitacaoAlteracaoPerfil.objects.filter(solicitante=sol).count(), 1
        )
        obj = SolicitacaoAlteracaoPerfil.objects.get(solicitante=sol)
        self.assertEqual(obj.status, StatusSolicitacaoPerfil.PENDENTE)
        self.assertEqual(obj.perfil_solicitado.codigo, "almoxarife")

    def test_nao_permite_segunda_solicitacao_pendente(self):
        sol = self._user("solicitante", "sol2-perfil@lab.test")
        almox = Perfil.objects.get(codigo="almoxarife")
        gestor = Perfil.objects.get(codigo="gestor")
        self.client.force_authenticate(user=sol)
        self.client.post(
            "/api/v1/auth/solicitacoes-perfil/",
            {"perfil_id": almox.id, "justificativa": "Primeira."},
            format="json",
        )
        response = self.client.post(
            "/api/v1/auth/solicitacoes-perfil/",
            {"perfil_id": gestor.id, "justificativa": "Segunda."},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_gestor_aprova_almoxarife(self):
        sol = self._user("solicitante", "sol3-perfil@lab.test")
        gestor = self._user("gestor", "gestor-sol@lab.test")
        almox = Perfil.objects.get(codigo="almoxarife")
        self.client.force_authenticate(user=sol)
        create = self.client.post(
            "/api/v1/auth/solicitacoes-perfil/",
            {"perfil_id": almox.id, "justificativa": "Preciso atender requisições."},
            format="json",
        )
        pk = create.data["id"]
        self.client.force_authenticate(user=gestor)
        response = self.client.post(
            f"/api/v1/auth/solicitacoes-perfil/{pk}/aprovar/",
            {"resposta_revisao": "Aprovado."},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sol.refresh_from_db()
        self.assertEqual(sol.perfil.codigo, "almoxarife")

    def test_gestor_nao_aprova_admin(self):
        sol = self._user("solicitante", "sol4-perfil@lab.test")
        gestor = self._user("gestor", "gestor2-sol@lab.test")
        admin_perfil = Perfil.objects.get(codigo="admin")
        self.client.force_authenticate(user=sol)
        create = self.client.post(
            "/api/v1/auth/solicitacoes-perfil/",
            {"perfil_id": admin_perfil.id, "justificativa": "Quero ser admin."},
            format="json",
        )
        pk = create.data["id"]
        self.client.force_authenticate(user=gestor)
        response = self.client.post(
            f"/api/v1/auth/solicitacoes-perfil/{pk}/aprovar/",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        sol.refresh_from_db()
        self.assertEqual(sol.perfil.codigo, "solicitante")

    def test_admin_aprova_admin(self):
        sol = self._user("solicitante", "sol5-perfil@lab.test")
        admin_user = self._user("admin", "admin-sol@lab.test")
        admin_perfil = Perfil.objects.get(codigo="admin")
        self.client.force_authenticate(user=sol)
        create = self.client.post(
            "/api/v1/auth/solicitacoes-perfil/",
            {"perfil_id": admin_perfil.id, "justificativa": "Substituo o coordenador."},
            format="json",
        )
        pk = create.data["id"]
        self.client.force_authenticate(user=admin_user)
        response = self.client.post(
            f"/api/v1/auth/solicitacoes-perfil/{pk}/aprovar/",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sol.refresh_from_db()
        self.assertEqual(sol.perfil.codigo, "admin")

    def test_solicitante_cancela_pendente(self):
        sol = self._user("solicitante", "sol6-perfil@lab.test")
        almox = Perfil.objects.get(codigo="almoxarife")
        self.client.force_authenticate(user=sol)
        create = self.client.post(
            "/api/v1/auth/solicitacoes-perfil/",
            {"perfil_id": almox.id, "justificativa": "Mudei de ideia depois."},
            format="json",
        )
        pk = create.data["id"]
        response = self.client.post(
            f"/api/v1/auth/solicitacoes-perfil/{pk}/cancelar/",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        obj = SolicitacaoAlteracaoPerfil.objects.get(pk=pk)
        self.assertEqual(obj.status, StatusSolicitacaoPerfil.CANCELADA)
