from django import forms
from .models import Produto

class ProdutoForm(forms.ModelForm):
 
    class Meta:
        model = Produto
        fields = ['nome', 'preco', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'preco': forms.NumberInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            
        }

    
    
    def clean_preco(self):
        preco = self.cleaned_data.get('preco')
        if preco is not None and preco <= 0:
            raise forms.ValidationError("O preço deve ser maior que zero.")
        return preco




    