from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class EmailBackend(ModelBackend):
    """
    Autentica utilizando o campo e-mail em vez de username.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        # No backend customizado, o que vem como 'username' pode ser o e-mail ou recebido por kwargs 'email'
        email = kwargs.get('email', username)
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
