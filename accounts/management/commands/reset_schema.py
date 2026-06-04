from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    help = (
        "Apaga e recria o schema public do PostgreSQL. "
        "Use apenas quando não houver dados a preservar."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--noinput",
            action="store_true",
            help="Não pedir confirmação interativa.",
        )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError(
                "Este comando só roda com DEBUG=True. Não use em produção."
            )

        if not options["noinput"]:
            confirm = input(
                "Isso apaga TODAS as tabelas do banco atual. Digite 'sim' para continuar: "
            )
            if confirm.strip().lower() != "sim":
                self.stdout.write("Operação cancelada.")
                return

        with connection.cursor() as cursor:
            cursor.execute("DROP SCHEMA public CASCADE")
            cursor.execute("CREATE SCHEMA public")
            cursor.execute("GRANT ALL ON SCHEMA public TO public")

        self.stdout.write(
            self.style.SUCCESS(
                "Schema reiniciado. Execute: python manage.py migrate"
            )
        )
