from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    name = forms.CharField(label="Nome completo", max_length=150, required=True)
    email = forms.EmailField(label="E-mail", max_length=254, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('name', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Um usuário com este e-mail já existe.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        # Usamos o e-mail como username interno do Django para facilitar
        user.username = self.cleaned_data['email']
        
        # Quebrar o 'name' em first_name e last_name
        full_name = self.cleaned_data['name'].split(' ', 1)
        user.first_name = full_name[0]
        if len(full_name) > 1:
            user.last_name = full_name[1]
            
        if commit:
            user.save()
        return user
