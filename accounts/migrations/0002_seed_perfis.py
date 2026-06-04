from django.db import migrations

PERFIS = [
    ("solicitante", "Solicitante", "Realiza requisições de itens."),
    ("admin", "Administrador", "Gerencia cadastros, permissões e configurações."),
    ("gestor", "Gestor", "Aprova requisições e supervisiona operações."),
    ("almoxarife", "Almoxarife", "Controla estoque e movimentações físicas."),
    (
        "tecnico_lab",
        "Técnico de Laboratório",
        "Opera equipamentos e realiza requisições internas.",
    ),
    (
        "tecnico_manutencao",
        "Técnico de Manutenção",
        "Executa ordens de serviço e manutenções.",
    ),
    ("auditor", "Auditor", "Consulta logs e relatórios de auditoria."),
    ("fiscal", "Fiscal", "Verifica conformidade regulatória."),
]


def seed_perfis(apps, schema_editor):
    Perfil = apps.get_model("accounts", "Perfil")
    for codigo, nome, descricao in PERFIS:
        Perfil.objects.get_or_create(
            codigo=codigo,
            defaults={"nome": nome, "descricao": descricao, "ativo": True},
        )


def unseed_perfis(apps, schema_editor):
    Perfil = apps.get_model("accounts", "Perfil")
    Perfil.objects.filter(codigo__in=[p[0] for p in PERFIS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_perfis, unseed_perfis),
    ]
