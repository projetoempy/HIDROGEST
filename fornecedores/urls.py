from django.urls import path
from .views import lista_fornecedores, cadastrar_fornecedor

urlpatterns = [
    path('listar/', lista_fornecedores, name='lista_fornecedores'),
    path('cadastrar/', cadastrar_fornecedor, name='cadastro_fornecedor'),
]