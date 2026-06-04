from django.conf import settings
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


class StatusSolicitacaoPerfil(models.TextChoices):
    PENDENTE = "pendente", "Pendente"
    APROVADA = "aprovada", "Aprovada"
    REJEITADA = "rejeitada", "Rejeitada"
    CANCELADA = "cancelada", "Cancelada"


class SolicitacaoAlteracaoPerfil(models.Model):
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="solicitacoes_alteracao_perfil",
    )
    perfil_atual = models.ForeignKey(
        Perfil,
        on_delete=models.PROTECT,
        related_name="solicitacoes_perfil_origem",
    )
    perfil_solicitado = models.ForeignKey(
        Perfil,
        on_delete=models.PROTECT,
        related_name="solicitacoes_perfil_destino",
    )
    justificativa = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=StatusSolicitacaoPerfil.choices,
        default=StatusSolicitacaoPerfil.PENDENTE,
    )
    revisado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="solicitacoes_perfil_revisadas",
    )
    resposta_revisao = models.TextField(blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    revisada_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "solicitação de alteração de perfil"
        verbose_name_plural = "solicitações de alteração de perfil"
        ordering = ["-criada_em"]
        constraints = [
            models.UniqueConstraint(
                fields=["solicitante"],
                condition=models.Q(status="pendente"),
                name="uniq_solicitacao_perfil_pendente_por_usuario",
            ),
        ]

    def __str__(self):
        return f"{self.solicitante.email} → {self.perfil_solicitado.codigo} ({self.status})"
