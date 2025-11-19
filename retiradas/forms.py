from django import forms
from .models import Retirada

class RetiradaForm(forms.ModelForm):
    class Meta:
        model = Retirada
        fields = ['quantidade']