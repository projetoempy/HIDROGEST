from django.db import models

# Create your models here.

class Fornecedor(models.Model):
    nome_empresa = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=20)
    endereco = models.CharField(max_length=200)
    site = models.URLField(blank=True)
    telefone = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.nome_empresa