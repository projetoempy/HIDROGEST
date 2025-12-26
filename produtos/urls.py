from django.urls import path
from . import views

urlpatterns = [
    path('produtos/', views.lista_produtos, name='lista_produtos'),
    path('produtos/novo/', views.cadastrar_produto, name='cadastrar_produto'),
    path('produtos/<int:id>/editar/', views.editar_produto, name='editar_produto'),
    path('produtos/<int:id>/excluir/', views.excluir_produto, name='excluir_produto'),
    path('produtos/<int:fornecedor_id>/', views.lista_produtos, name='lista_produtos'),

    

    path('produtos/<int:fornecedor_id>/novo/', views.cadastrar_produto, name='cadastrar_produto_fornecedor'),
]

