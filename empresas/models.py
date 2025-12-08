from django.db import models

# Create your models here.
class Empresa(models.Model):
    nome = models.CharField(max_length=150)
    endereco = models.CharField(max_length=255)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)

    def __str__(self):
        return self.nome