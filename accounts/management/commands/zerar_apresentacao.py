from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from accounts.models import Perfil

User = get_user_model()

SENHA_DEMO = "SenhaSegura123!"

USUARIOS_DEMO = (
    ("admin@lab.test", "Admin", "admin", True),
    ("gestor@lab.test", "Gestor Demo", "gestor", False),
    ("almox@lab.test", "Almoxarife Demo", "almoxarife", False),
    ("aluno@lab.test", "Solicitante Demo", "solicitante", False),
)


class Command(BaseCommand):
    help = (
        "Zera o banco (schema), aplica migrações e recria usuários padrão para ensaio de apresentação. "
        "Só roda com DEBUG=True."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--noinput",
            action="store_true",
            help="Não pedir confirmação interativa.",
        )
        parser.add_argument(
            "--password",
            default=SENHA_DEMO,
            help=f"Senha dos usuários demo (padrão: {SENHA_DEMO}).",
        )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Este comando só roda com DEBUG=True.")

        if not options["noinput"]:
            confirm = input(
                "Isso apaga TODOS os dados do banco e recria usuários de demo. "
                "Digite 'sim' para continuar: "
            )
            if confirm.strip().lower() != "sim":
                self.stdout.write("Operação cancelada.")
                return

        password = options["password"]

        self.stdout.write("Reiniciando schema PostgreSQL…")
        call_command("reset_schema", "--noinput")

        self.stdout.write("Aplicando migrações…")
        call_command("migrate", "--noinput")

        self.stdout.write("Criando usuários de apresentação…")
        for email, nome, codigo_perfil, superuser in USUARIOS_DEMO:
            perfil = Perfil.objects.get(codigo=codigo_perfil)
            if superuser:
                User.objects.create_superuser(
                    email=email,
                    password=password,
                    nome=nome,
                    perfil=perfil,
                )
            else:
                User.objects.create_user(
                    email=email,
                    password=password,
                    nome=nome,
                    perfil=perfil,
                )
            self.stdout.write(f"  · {email} ({codigo_perfil})")

        self.stdout.write(
            self.style.SUCCESS(
                "\nBanco zerado. Próximo passo: login como almox@lab.test e cadastrar "
                "categoria, unidade, local, itens e entrada (ver guia-apresentacao-cliente.md §6)."
            )
        )
        self.stdout.write(f"Senha de todos os usuários demo: {password}")
