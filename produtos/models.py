from django.db import models

# Create your models here.
from fornecedores.models import Fornecedor
class Produto(models.Model):
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, related_name="produtos")
    nome = models.CharField(max_length=150)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.TextField(blank=True, null=True)
    imagem = models.ImageField(upload_to='produtos/', null=True, blank=True)

    def __str__(self):
        return f"{self.nome} ({self.fornecedor.nome})"