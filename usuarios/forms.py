from django import forms
from .models import Usuario

class CadastroFuncionarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'telefone', 'endereco', 'password']