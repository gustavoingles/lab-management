from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from accounts.models import Perfil

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
