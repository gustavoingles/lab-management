from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Perfil
from inventory.choices import StatusRequisicao, StatusReservaEquipamento, TipoMovimentacao
from inventory.models import (
    Categoria,
    Equipamento,
    Estoque,
    Item,
    Localizacao,
    ReservaEquipamento,
)

User = get_user_model()


class ReservaEstoqueAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        for codigo, nome in [
            ("almoxarife", "Almoxarife"),
            ("gestor", "Gestor"),
            ("solicitante", "Solicitante"),
        ]:
            Perfil.objects.get_or_create(
                codigo=codigo, defaults={"nome": nome, "descricao": "", "ativo": True}
            )
        cls.almoxarife = User.objects.create_user(
            email="almox2@lab.test",
            password="SenhaSegura123!",
            nome="Almox",
            perfil=Perfil.objects.get(codigo="almoxarife"),
        )
        cls.gestor = User.objects.create_user(
            email="gestor2@lab.test",
            password="SenhaSegura123!",
            nome="Gestor",
            perfil=Perfil.objects.get(codigo="gestor"),
        )
        cls.solicitante = User.objects.create_user(
            email="sol3@lab.test",
            password="SenhaSegura123!",
            nome="Sol",
            perfil=Perfil.objects.get(codigo="solicitante"),
        )
        cat = Categoria.objects.create(codigo="INS2", nome="Insumos 2")
        cls.local = Localizacao.objects.create(
            nome="Lab Reserva", tipo="laboratorio", codigo="LR1"
        )
        cls.item = Item.objects.create(
            codigo_interno="RES-001",
            nome="Reagente Reserva",
            categoria=cat,
            tipo_item="reagente",
        )

    def test_aprovar_requisicao_reserva_estoque(self):
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
        self.client.force_authenticate(user=self.solicitante)
        req = self.client.post(
            "/api/v1/requisicoes/",
            {"finalidade": "Teste reserva", "prioridade": "media"},
            format="json",
        ).data["id"]
        self.client.post(
            "/api/v1/requisicao-itens/",
            {
                "requisicao": req,
                "item": self.item.id,
                "quantidade_solicitada": "3.000",
            },
            format="json",
        )
        self.client.force_authenticate(user=self.gestor)
        aprovar = self.client.post(f"/api/v1/requisicoes/{req}/aprovar/")
        self.assertEqual(aprovar.status_code, status.HTTP_200_OK)
        estoque = Estoque.objects.get(item=self.item, localizacao=self.local)
        self.assertEqual(estoque.quantidade_reservada, Decimal("3.000"))
        self.assertEqual(estoque.saldo_livre, Decimal("7.000"))

    def test_rejeitar_libera_reserva(self):
        self.client.force_authenticate(user=self.almoxarife)
        self.client.post(
            "/api/v1/movimentacoes/",
            {
                "item_id": self.item.id,
                "tipo_movimentacao": TipoMovimentacao.ENTRADA,
                "quantidade": "5.000",
                "localizacao_destino_id": self.local.id,
            },
            format="json",
        )
        self.client.force_authenticate(user=self.solicitante)
        req = self.client.post(
            "/api/v1/requisicoes/",
            {"finalidade": "Rejeitar reserva", "prioridade": "media"},
            format="json",
        ).data["id"]
        self.client.post(
            "/api/v1/requisicao-itens/",
            {"requisicao": req, "item": self.item.id, "quantidade_solicitada": "2.000"},
            format="json",
        )
        self.client.force_authenticate(user=self.gestor)
        self.client.post(f"/api/v1/requisicoes/{req}/aprovar/")
        self.client.post(
            f"/api/v1/requisicoes/{req}/rejeitar/", {"motivo": "cancelou"}, format="json"
        )
        estoque = Estoque.objects.get(item=self.item, localizacao=self.local)
        self.assertEqual(estoque.quantidade_reservada, Decimal("0"))


class ReservaEquipamentoAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        for codigo, nome in [("gestor", "Gestor"), ("solicitante", "Solicitante")]:
            Perfil.objects.get_or_create(
                codigo=codigo, defaults={"nome": nome, "descricao": "", "ativo": True}
            )
        cls.gestor = User.objects.create_user(
            email="gestor3@lab.test",
            password="SenhaSegura123!",
            nome="Gestor",
            perfil=Perfil.objects.get(codigo="gestor"),
        )
        cls.solicitante = User.objects.create_user(
            email="sol4@lab.test",
            password="SenhaSegura123!",
            nome="Sol",
            perfil=Perfil.objects.get(codigo="solicitante"),
        )
        cat = Categoria.objects.create(codigo="EQP", nome="Equip")
        item = Item.objects.create(
            codigo_interno="MIC-01",
            nome="Microscópio",
            categoria=cat,
            tipo_item="equipamento",
        )
        cls.equipamento = Equipamento.objects.create(
            item=item, numero_serie="MIC-001", tombamento="T001"
        )

    def test_reserva_equipamento_conflito(self):
        agora = timezone.now()
        ReservaEquipamento.objects.create(
            equipamento=self.equipamento,
            solicitante=self.solicitante,
            finalidade="Aula",
            inicio=agora + timedelta(hours=1),
            fim=agora + timedelta(hours=3),
            status=StatusReservaEquipamento.CONFIRMADA,
        )
        self.client.force_authenticate(user=self.solicitante)
        response = self.client.post(
            "/api/v1/reservas-equipamento/",
            {
                "equipamento": self.equipamento.id,
                "finalidade": "Conflito",
                "inicio": (agora + timedelta(hours=2)).isoformat(),
                "fim": (agora + timedelta(hours=4)).isoformat(),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fluxo_reserva_equipamento(self):
        agora = timezone.now()
        self.client.force_authenticate(user=self.solicitante)
        create = self.client.post(
            "/api/v1/reservas-equipamento/",
            {
                "equipamento": self.equipamento.id,
                "finalidade": "Pesquisa",
                "inicio": (agora + timedelta(days=1)).isoformat(),
                "fim": (agora + timedelta(days=1, hours=2)).isoformat(),
            },
            format="json",
        )
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        pk = create.data["id"]
        self.client.force_authenticate(user=self.gestor)
        aprovar = self.client.post(f"/api/v1/reservas-equipamento/{pk}/aprovar/")
        self.assertEqual(aprovar.status_code, status.HTTP_200_OK)
        self.assertEqual(aprovar.data["status"], StatusReservaEquipamento.CONFIRMADA)
