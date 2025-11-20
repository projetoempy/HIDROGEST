from django.db import models

# Create your models here.

from produtos.models import Produto
from fornecedores.models import Fornecedor

class ListaCompra(models.Model):
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE)
    data_criacao = models.DateTimeField(auto_now_add=True)
    recebido = models.BooleanField(default=False)

class ItemCompra(models.Model):
    lista = models.ForeignKey(ListaCompra, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade_desejada = models.PositiveIntegerField()
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)