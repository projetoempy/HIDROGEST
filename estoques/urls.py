from django.urls import path
from . import views

urlpatterns = [
    path('estoques/', views.lista_estoques, name='lista_estoques'),
    path('estoques/novo/', views.adicionar_estoque, name='adicionar_estoque'),
    path('retiradas/', views.log_retiradas, name='log_retiradas'),
    path('estoques/<int:id>/editar/', views.editar_estoque, name='editar_estoque'),
    path('estoques/<int:id>/excluir/', views.excluir_estoque, name='excluir_estoque'),
    path('entradas/', views.log_entradas, name='log_entradas'),
    path('estoques/<int:id>/retirar/', views.retirar_estoque, name='retirar_estoque'),
]