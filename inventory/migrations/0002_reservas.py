import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="requisicaoitem",
            name="localizacao_reserva",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="requisicoes_reservadas",
                to="inventory.localizacao",
            ),
        ),
        migrations.CreateModel(
            name="ReservaEquipamento",
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
                ("finalidade", models.TextField()),
                ("inicio", models.DateTimeField()),
                ("fim", models.DateTimeField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pendente", "Pendente"),
                            ("confirmada", "Confirmada"),
                            ("cancelada", "Cancelada"),
                            ("encerrada", "Encerrada"),
                        ],
                        default="pendente",
                        max_length=20,
                    ),
                ),
                ("observacao", models.TextField(blank=True)),
                ("criada_em", models.DateTimeField(auto_now_add=True)),
                ("atualizada_em", models.DateTimeField(auto_now=True)),
                (
                    "aprovador",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="reservas_equipamento_aprovadas",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "equipamento",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reservas",
                        to="inventory.equipamento",
                    ),
                ),
                (
                    "solicitante",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reservas_equipamento",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "reserva de equipamento",
                "verbose_name_plural": "reservas de equipamento",
                "ordering": ["-inicio"],
            },
        ),
    ]
