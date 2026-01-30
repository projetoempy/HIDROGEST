from django.contrib import admin

# Register your models here.

from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'empresa', 'tipo_usuario', 'status_ativo')
    list_filter = ('tipo_usuario', 'status_ativo', 'empresa')
    search_fields = ('username', 'email')
