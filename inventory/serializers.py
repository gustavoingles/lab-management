from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from inventory.models import (
    Auditoria,
    Baixa,
    Categoria,
    Equipamento,
    Estoque,
    Inventario,
    InventarioItem,
    Item,
    Localizacao,
    Lote,
    Manutencao,
    Movimentacao,
    OrdemServico,
    Requisicao,
    RequisicaoItem,
    ReservaEquipamento,
    UnidadeMedida,
)

User = get_user_model()


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = "__all__"


class UnidadeMedidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadeMedida
        fields = "__all__"


class LocalizacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Localizacao
        fields = "__all__"


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = "__all__"


class EquipamentoSerializer(serializers.ModelSerializer):
    item_detail = ItemSerializer(source="item", read_only=True)

    class Meta:
        model = Equipamento
        fields = "__all__"


class EstoqueSerializer(serializers.ModelSerializer):
    abaixo_alerta = serializers.BooleanField(read_only=True)
    saldo_livre = serializers.SerializerMethodField()

    def get_saldo_livre(self, obj):
        return obj.saldo_livre
    item_nome = serializers.CharField(source="item.nome", read_only=True)
    localizacao_nome = serializers.CharField(source="localizacao.nome", read_only=True)

    class Meta:
        model = Estoque
        fields = "__all__"


class LoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lote
        fields = "__all__"


class RequisicaoItemSerializer(serializers.ModelSerializer):
    item_nome = serializers.CharField(source="item.nome", read_only=True)
    localizacao_reserva_nome = serializers.CharField(
        source="localizacao_reserva.nome", read_only=True, default=None
    )

    class Meta:
        model = RequisicaoItem
        fields = "__all__"


class RequisicaoSerializer(serializers.ModelSerializer):
    itens = RequisicaoItemSerializer(many=True, read_only=True)
    solicitante_nome = serializers.CharField(source="solicitante.nome", read_only=True)

    class Meta:
        model = Requisicao
        fields = "__all__"
        read_only_fields = (
            "solicitante",
            "aprovador",
            "data_solicitacao",
            "data_aprovacao",
            "data_atendimento",
        )

    def create(self, validated_data):
        validated_data["solicitante"] = self.context["request"].user
        return super().create(validated_data)


class RequisicaoItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequisicaoItem
        fields = "__all__"


class OrdemServicoSerializer(serializers.ModelSerializer):
    equipamento_serie = serializers.CharField(
        source="equipamento.numero_serie", read_only=True
    )

    class Meta:
        model = OrdemServico
        fields = "__all__"


class ManutencaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manutencao
        fields = "__all__"


class InventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventario
        fields = "__all__"


class InventarioItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventarioItem
        fields = "__all__"


class BaixaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Baixa
        fields = "__all__"

    def create(self, validated_data):
        validated_data["usuario"] = self.context["request"].user
        return super().create(validated_data)


class MovimentacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movimentacao
        fields = "__all__"
        read_only_fields = (
            "usuario",
            "saldo_resultante",
            "created_at",
            "requisicao_item",
            "ordem_servico",
            "inventario_item",
            "baixa",
        )


class MovimentacaoCreateSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    tipo_movimentacao = serializers.CharField()
    quantidade = serializers.DecimalField(max_digits=14, decimal_places=3)
    localizacao_origem_id = serializers.IntegerField(required=False, allow_null=True)
    localizacao_destino_id = serializers.IntegerField(required=False, allow_null=True)
    lote_id = serializers.IntegerField(required=False, allow_null=True)
    motivo = serializers.CharField(required=False, allow_blank=True)
    observacao = serializers.CharField(required=False, allow_blank=True)


class AtenderRequisicaoItemSerializer(serializers.Serializer):
    localizacao_origem_id = serializers.IntegerField()
    lote_id = serializers.IntegerField(required=False, allow_null=True)


class EncerrarOrdemServicoSerializer(serializers.Serializer):
    laudo_emitido = serializers.BooleanField(default=False)
    status_equipamento = serializers.CharField(required=False)


class ReservaEquipamentoSerializer(serializers.ModelSerializer):
    equipamento_serie = serializers.CharField(
        source="equipamento.numero_serie", read_only=True
    )
    solicitante_nome = serializers.CharField(source="solicitante.nome", read_only=True)

    class Meta:
        model = ReservaEquipamento
        fields = "__all__"
        read_only_fields = ("solicitante", "aprovador", "criada_em", "atualizada_em")

    def create(self, validated_data):
        from inventory.services.reservas_equipamento import criar_reserva_equipamento

        equipamento = validated_data.pop("equipamento")
        try:
            return criar_reserva_equipamento(
                solicitante=self.context["request"].user,
                equipamento_id=equipamento.pk,
                finalidade=validated_data["finalidade"],
                inicio=validated_data["inicio"],
                fim=validated_data["fim"],
                observacao=validated_data.get("observacao", ""),
            )
        except DjangoValidationError as exc:
            if hasattr(exc, "message_dict") and exc.message_dict:
                raise serializers.ValidationError(exc.message_dict) from exc
            raise serializers.ValidationError(list(exc.messages)) from exc


class AuditoriaSerializer(serializers.ModelSerializer):
    usuario_nome = serializers.CharField(source="usuario.nome", read_only=True)

    class Meta:
        model = Auditoria
        fields = "__all__"
