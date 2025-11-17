from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    TIPO_CHOICES = [('gerente', 'Gerente'), ('funcionario', 'Funcionário')]
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    telefone = models.CharField(max_length=20)
    endereco = models.CharField(max_length=200)
    status_ativo = models.BooleanField(default=False)