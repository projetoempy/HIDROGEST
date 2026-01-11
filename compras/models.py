from django.db import models

# Create your models here.

from usuarios.models import Empresa, Usuario
from produtos.models import Produto

class ListaCompra(models.Model):
    STATUS = [
        ('EM_CRIACAO', 'Em Criação'),
        ('EM_PROCESSO_AUTORIZACAO', 'Em processo de autorização'),
        ('AUTORIZADA', 'Autorizada'),
        ('UNIDA', 'Unida'),
        ('EM_PROCESSO_CONSOLIDACAO', 'Em processo de consolidação'),
        ('CONSOLIDADA', 'Consolidada'),
        ('EM_PROCESSO_COMPRA', 'Em Processo de Compra'),
        ('EM_ENTREGA', 'Em Rota de Entrega'),
        ('RECEBIDA', 'Itens Recebidos'),
    ]

    numero = models.CharField(max_length=20, unique=False)  # Ex: 00001/2025
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="listas_compra")
    status = models.CharField(max_length=30, choices=STATUS, default='EM_CRIACAO')
    criado_por = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="listas_criadas")
    data_criacao = models.DateTimeField(auto_now_add=True)
    listas_unidas = models.ManyToManyField("self", blank=True, symmetrical=False, related_name="lista_principal")

    class Meta:
        unique_together = ('empresa', 'numero')  # garante unicidade por empresa


    def __str__(self):
        return f"Lista {self.numero} - {self.empresa.nome}"


class ItemListaCompra(models.Model):
    lista = models.ForeignKey(ListaCompra, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade_desejada = models.PositiveIntegerField(default=0)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) # Para armazenar o preço no momento da compra


    def __str__(self):
        return f"{self.produto.nome} ({self.quantidade_desejada})"


class LogAlteracaoLista(models.Model):
    lista = models.ForeignKey(ListaCompra, on_delete=models.CASCADE, related_name="alteracoes")
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    alterado_por = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    quantidade_antiga = models.PositiveIntegerField()
    quantidade_nova = models.PositiveIntegerField()
    data_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Alteração {self.produto.nome}: {self.quantidade_antiga} → {self.quantidade_nova}"