from django.db import models

# Create your models here.
from django.db import models

class Fornecedor(models.Model):
    nome = models.CharField(max_length=150)
    cnpj = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    site = models.URLField(blank=True, null=True)
    endereco = models.CharField(max_length=255)

    def __str__(self):
        return self.nome


