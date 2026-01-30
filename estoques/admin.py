from django.contrib import admin

# Register your models here.

from .models import Estoque, LogRetirada, LogEntrada

@admin.register(Estoque)
class EstoqueAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'produto', 'quantidade', 'quantidade_minima')
    list_filter = ('empresa', 'produto')

@admin.register(LogRetirada)
class LogRetiradaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'empresa', 'produto', 'quantidade', 'data_hora')
    list_filter = ('empresa', 'usuario')
    search_fields = ('produto__nome', 'usuario__username')

@admin.register(LogEntrada)
class LogEntradaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'empresa', 'produto', 'quantidade', 'data_hora')
    list_filter = ('empresa', 'usuario')
    search_fields = ('produto__nome', 'usuario__username')