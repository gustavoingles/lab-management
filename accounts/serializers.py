from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from accounts.models import Perfil, SolicitacaoAlteracaoPerfil
from accounts.services.solicitacao_perfil import criar_solicitacao
from accounts.permissions import PERFIL_ADMIN, PERFIL_GESTOR, PERFIS_GESTAO

User = get_user_model()


class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = ("id", "codigo", "nome")


class UserSerializer(serializers.ModelSerializer):
    perfil = PerfilSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "nome",
            "email",
            "matricula",
            "cargo",
            "perfil",
            "is_active",
            "date_joined",
        )
        read_only_fields = fields


class UserUpdateSerializer(serializers.ModelSerializer):
    perfil_id = serializers.PrimaryKeyRelatedField(
        queryset=Perfil.objects.filter(ativo=True),
        source="perfil",
    )

    class Meta:
        model = User
        fields = ("nome", "matricula", "cargo", "perfil_id", "is_active")

    def validate_perfil_id(self, perfil: Perfil):
        request = self.context.get("request")
        if not request:
            return perfil

        actor = request.user
        if actor.is_superuser:
            return perfil

        actor_codigo = actor.perfil.codigo
        target = self.instance

        if perfil.codigo == PERFIL_ADMIN and actor_codigo != PERFIL_ADMIN:
            raise serializers.ValidationError(
                "Apenas usuários com perfil admin podem atribuir o perfil admin."
            )

        if target and target.perfil.codigo == PERFIL_ADMIN and actor_codigo != PERFIL_ADMIN:
            raise serializers.ValidationError(
                "Apenas admin pode alterar usuários que já possuem perfil admin."
            )

        if target and target.pk == actor.pk and perfil.codigo in PERFIS_GESTAO:
            if actor_codigo != PERFIL_ADMIN:
                raise serializers.ValidationError(
                    "Você não pode elevar seu próprio perfil para gestão."
                )

        return perfil

    def validate_is_active(self, value: bool):
        request = self.context.get("request")
        if not request or not self.instance:
            return value
        if (
            self.instance.pk == request.user.pk
            and not value
            and not request.user.is_superuser
        ):
            raise serializers.ValidationError("Você não pode desativar sua própria conta.")
        return value


class SolicitacaoAlteracaoPerfilSerializer(serializers.ModelSerializer):
    perfil_atual = PerfilSerializer(read_only=True)
    perfil_solicitado = PerfilSerializer(read_only=True)
    solicitante_nome = serializers.CharField(source="solicitante.nome", read_only=True)
    solicitante_email = serializers.CharField(source="solicitante.email", read_only=True)

    class Meta:
        model = SolicitacaoAlteracaoPerfil
        fields = (
            "id",
            "solicitante",
            "solicitante_nome",
            "solicitante_email",
            "perfil_atual",
            "perfil_solicitado",
            "justificativa",
            "status",
            "resposta_revisao",
            "criada_em",
            "revisada_em",
        )
        read_only_fields = (
            "id",
            "solicitante",
            "perfil_atual",
            "status",
            "resposta_revisao",
            "criada_em",
            "revisada_em",
        )


class SolicitacaoAlteracaoPerfilCreateSerializer(serializers.Serializer):
    perfil_id = serializers.PrimaryKeyRelatedField(
        queryset=Perfil.objects.filter(ativo=True),
        source="perfil_solicitado",
    )
    justificativa = serializers.CharField()

    def create(self, validated_data):
        request = self.context["request"]
        return criar_solicitacao(
            usuario=request.user,
            perfil_solicitado=validated_data["perfil_solicitado"],
            justificativa=validated_data["justificativa"],
        )


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "nome",
            "email",
            "password",
            "password_confirm",
            "matricula",
            "cargo",
        )

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Um usuário com este e-mail já existe.")
        return value.lower()

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "As senhas não coincidem."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        perfil = Perfil.objects.get(codigo="solicitante")
        user = User(perfil=perfil, **validated_data)
        user.set_password(password)
        user.save()
        return user
