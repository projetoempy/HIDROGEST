from django.db import models

# Create your models here.

from usuarios.models import Empresa, Usuario
from produtos.models import Produto

class Estoque(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="estoques")
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name="estoques")
    quantidade = models.PositiveIntegerField(default=0)
    quantidade_minima = models.PositiveIntegerField(default=0)
    class Meta:
        unique_together = ('empresa', 'produto')

    def __str__(self):
        return f"{self.empresa.nome} - {self.produto.nome}"


class LogRetirada(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="retiradas")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="retiradas")
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name="retiradas")
    destino = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="retiradas_destino", null=True, blank=True)
    quantidade = models.PositiveIntegerField()
    data_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} retirou {self.quantidade} de {self.produto.nome} ({self.empresa.nome})"


class LogEntrada(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="entradas")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="entradas")
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name="entradas")
    quantidade = models.PositiveIntegerField()
    data_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} recebeu {self.quantidade} de {self.produto.nome} ({self.empresa.nome})"