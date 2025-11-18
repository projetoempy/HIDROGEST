from django import forms
from .models import Usuario

class CadastroFuncionarioForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Senha"
        )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirme a senha"
    )
    username = forms.CharField(
        label="Usuário",
        max_length=150,
        help_text="Digite um nome de usuário válido (sem espaços ou caracteres especiais).")

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'telefone', 'endereco', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "As senhas não coincidem.")

