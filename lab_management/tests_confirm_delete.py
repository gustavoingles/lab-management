from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from accounts.models import Perfil
from inventory.models import Categoria, Item, UnidadeMedida

User = get_user_model()


class ConfirmDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Perfil.objects.get_or_create(
            codigo="almoxarife",
            defaults={"nome": "Almoxarife", "descricao": "", "ativo": True},
        )
        cls.user = User.objects.create_user(
            email="almox@lab.test",
            password="SenhaSegura123!",
            nome="Almox",
            perfil=Perfil.objects.get(codigo="almoxarife"),
        )

    def test_excluir_unidade_com_item_vinculado_redireciona_com_erro(self):
        unidade = UnidadeMedida.objects.create(nome="Litro", sigla="L")
        categoria = Categoria.objects.create(codigo="CAT", nome="Cat")
        Item.objects.create(
            codigo_interno="X-001",
            nome="Reagente 1",
            categoria=categoria,
            unidade_medida=unidade,
            tipo_item="reagente",
        )
        self.client.force_login(self.user)
        url = reverse("app:unidade_medida_excluir", kwargs={"pk": unidade.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("app:unidades_medida"))
        self.assertTrue(UnidadeMedida.objects.filter(pk=unidade.pk).exists())
        msgs = [m.message for m in get_messages(response.wsgi_request)]
        self.assertTrue(any("registros vinculados" in m for m in msgs))
