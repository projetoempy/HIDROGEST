from django.contrib import admin

# Register your models here.
from .models import ListaCompra, ItemCompra

admin.site.register(ListaCompra)
admin.site.register(ItemCompra)