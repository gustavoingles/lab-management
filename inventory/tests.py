from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Perfil
from inventory.choices import StatusRequisicao, TipoMovimentacao
from inventory.models import Categoria, Estoque, Item, Localizacao, Lote

User = get_user_model()


class InventoryAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        Perfil.objects.get_or_create(
            codigo="almoxarife",
            defaults={"nome": "Almoxarife", "descricao": "", "ativo": True},
        )
        Perfil.objects.get_or_create(
            codigo="gestor",
            defaults={"nome": "Gestor", "descricao": "", "ativo": True},
        )
        Perfil.objects.get_or_create(
            codigo="solicitante",
            defaults={"nome": "Solicitante", "descricao": "", "ativo": True},
        )
        cls.almoxarife = User.objects.create_user(
            email="almox@lab.test",
            password="SenhaSegura123!",
            nome="Almox",
            perfil=Perfil.objects.get(codigo="almoxarife"),
        )
        cls.gestor = User.objects.create_user(
            email="gestor@lab.test",
            password="SenhaSegura123!",
            nome="Gestor",
            perfil=Perfil.objects.get(codigo="gestor"),
        )
        cls.solicitante = User.objects.create_user(
            email="sol@lab.test",
            password="SenhaSegura123!",
            nome="Sol",
            perfil=Perfil.objects.get(codigo="solicitante"),
        )
        cls.categoria = Categoria.objects.create(codigo="INS", nome="Insumos")
        cls.local = Localizacao.objects.create(
            nome="Lab 1", tipo="laboratorio", codigo="L1"
        )
        cls.item = Item.objects.create(
            codigo_interno="ITEM-001",
            nome="Reagente A",
            categoria=cls.categoria,
            tipo_item="reagente",
        )

    def test_movimentacao_entrada_atualiza_estoque(self):
        self.client.force_authenticate(user=self.almoxarife)
        response = self.client.post(
            "/api/v1/movimentacoes/",
            {
                "item_id": self.item.id,
                "tipo_movimentacao": TipoMovimentacao.ENTRADA,
                "quantidade": "10.000",
                "localizacao_destino_id": self.local.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        estoque = Estoque.objects.get(item=self.item, localizacao=self.local)
        self.assertEqual(estoque.quantidade_disponivel, Decimal("10.000"))

    def test_fluxo_requisicao_aprovacao_atendimento(self):
        self.client.force_authenticate(user=self.solicitante)
        req_resp = self.client.post(
            "/api/v1/requisicoes/",
            {"finalidade": "Experimento", "prioridade": "media"},
            format="json",
        )
        self.assertEqual(req_resp.status_code, status.HTTP_201_CREATED)
        req_id = req_resp.data["id"]
        self.client.post(
            "/api/v1/requisicao-itens/",
            {
                "requisicao": req_id,
                "item": self.item.id,
                "quantidade_solicitada": "2.000",
            },
            format="json",
        )
        self.client.force_authenticate(user=self.almoxarife)
        self.client.post(
            "/api/v1/movimentacoes/",
            {
                "item_id": self.item.id,
                "tipo_movimentacao": TipoMovimentacao.ENTRADA,
                "quantidade": "10.000",
                "localizacao_destino_id": self.local.id,
            },
            format="json",
        )
        self.client.force_authenticate(user=self.gestor)
        aprovar = self.client.post(f"/api/v1/requisicoes/{req_id}/aprovar/")
        self.assertEqual(aprovar.status_code, status.HTTP_200_OK)
        linha = aprovar.data["itens"][0]
        self.client.force_authenticate(user=self.almoxarife)
        atender = self.client.post(
            f"/api/v1/requisicao-itens/{linha['id']}/atender/",
            {"localizacao_origem_id": self.local.id},
            format="json",
        )
        self.assertEqual(atender.status_code, status.HTTP_200_OK)
        req = self.client.get(f"/api/v1/requisicoes/{req_id}/")
        self.assertEqual(req.data["status"], StatusRequisicao.ATENDIDA)

    def test_estoque_alertas(self):
        Estoque.objects.create(
            item=self.item,
            localizacao=self.local,
            quantidade_disponivel=Decimal("1"),
            nivel_alerta=Decimal("5"),
            nivel_minimo=Decimal("2"),
        )
        self.client.force_authenticate(user=self.almoxarife)
        response = self.client.get("/api/v1/estoques/alertas/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
