import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_seed_perfis"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SolicitacaoAlteracaoPerfil",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("justificativa", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pendente", "Pendente"),
                            ("aprovada", "Aprovada"),
                            ("rejeitada", "Rejeitada"),
                            ("cancelada", "Cancelada"),
                        ],
                        default="pendente",
                        max_length=20,
                    ),
                ),
                ("resposta_revisao", models.TextField(blank=True)),
                ("criada_em", models.DateTimeField(auto_now_add=True)),
                ("revisada_em", models.DateTimeField(blank=True, null=True)),
                (
                    "perfil_atual",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="solicitacoes_perfil_origem",
                        to="accounts.perfil",
                    ),
                ),
                (
                    "perfil_solicitado",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="solicitacoes_perfil_destino",
                        to="accounts.perfil",
                    ),
                ),
                (
                    "revisado_por",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="solicitacoes_perfil_revisadas",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "solicitante",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="solicitacoes_alteracao_perfil",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "solicitação de alteração de perfil",
                "verbose_name_plural": "solicitações de alteração de perfil",
                "ordering": ["-criada_em"],
            },
        ),
        migrations.AddConstraint(
            model_name="solicitacaoalteracaoperfil",
            constraint=models.UniqueConstraint(
                condition=models.Q(("status", "pendente")),
                fields=("solicitante",),
                name="uniq_solicitacao_perfil_pendente_por_usuario",
            ),
        ),
    ]
