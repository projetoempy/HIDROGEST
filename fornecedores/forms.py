from django import forms
from .models import Fornecedor

class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = ['nome_empresa', 'cnpj', 'email', 'telefone', 'endereco', 'site']
        widgets = {
            'endereco': forms.Textarea(attrs={'rows': 3}),
        }