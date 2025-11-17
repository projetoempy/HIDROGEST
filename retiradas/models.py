from django.db import models

# Create your models here.

from usuarios.models import Usuario
from produtos.models import Produto

class Retirada(models.Model):
    funcionario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    data_hora = models.DateTimeField(auto_now_add=True)