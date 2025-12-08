from django.urls import path
from . import views

urlpatterns = [
    path('fornecedores/', views.lista_fornecedores, name='lista_fornecedores'),
    path('fornecedores/novo/', views.cadastrar_fornecedor, name='cadastrar_fornecedor'),
    path('fornecedores/<int:id>/editar/', views.editar_fornecedor, name='editar_fornecedor'),
    path('fornecedores/<int:id>/excluir/', views.excluir_fornecedor, name='excluir_fornecedor'),
]