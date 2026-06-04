from django.contrib.auth.models import AbstractUser
from django.db import models

from accounts.managers import UsuarioManager


class Perfil(models.Model):
    codigo = models.CharField(max_length=40, unique=True)
    nome = models.CharField(max_length=120, unique=True)
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "perfil"
        verbose_name_plural = "perfis"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Usuario(AbstractUser):
    username = None
    first_name = None
    last_name = None

    nome = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    matricula = models.CharField(max_length=60, unique=True, null=True, blank=True)
    perfil = models.ForeignKey(
        Perfil,
        on_delete=models.PROTECT,
        related_name="usuarios",
    )
    cargo = models.CharField(max_length=120, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome"]

    objects = UsuarioManager()

    class Meta:
        verbose_name = "usuário"
        verbose_name_plural = "usuários"
        ordering = ["nome"]

    def __str__(self):
        return self.nome
