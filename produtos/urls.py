from django.urls import path
from .views import cadastrar_produto, editar_produto, excluir_produto

urlpatterns = [
    path('cadastrar/<int:fornecedor_id>/', cadastrar_produto, name='cadastrar_produto'),
    path('editar/<int:produto_id>/', editar_produto, name='editar_produto'),
    path('excluir/<int:produto_id>/', excluir_produto, name='excluir_produto'),
]