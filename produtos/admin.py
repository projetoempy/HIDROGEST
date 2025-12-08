from django.contrib import admin

# Register your models here.
from .models import Produto

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'fornecedor', 'preco')
    list_filter = ('fornecedor',)
    search_fields = ('nome',)