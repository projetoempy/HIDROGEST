from django.db import models

# Create your models here.

from produtos.models import Produto

class Estoque(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    quantidade_minima = models.PositiveIntegerField()
    data_cadastro = models.DateTimeField(auto_now_add=True)