from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from accounts.models import Perfil

User = get_user_model()


class Command(BaseCommand):
    help = "Cria um superusuário vinculado ao perfil admin (após migrate)."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True)
        parser.add_argument("--nome", required=True)
        parser.add_argument("--password", required=True)

    def handle(self, *args, **options):
        try:
            perfil = Perfil.objects.get(codigo="admin")
        except Perfil.DoesNotExist as exc:
            raise CommandError(
                "Perfil 'admin' não encontrado. Execute: python manage.py migrate"
            ) from exc

        email = options["email"].lower()
        if User.objects.filter(email=email).exists():
            raise CommandError(f"Usuário com e-mail {email} já existe.")

        User.objects.create_superuser(
            email=email,
            password=options["password"],
            nome=options["nome"],
            perfil=perfil,
        )
        self.stdout.write(self.style.SUCCESS(f"Superusuário {email} criado."))
