from django.urls import path
from . import views

urlpatterns = [
    path('listas/', views.lista_compras, name='lista_compras'),
    path('listas/nova/', views.criar_lista, name='criar_lista'),
    path('listas/unir/', views.unir_listas, name='unir_listas'),
    path('listas/<int:id>/detalhes/', views.detalhes_lista, name='detalhes_lista'),
    path('listas/<int:id>/excluir/', views.excluir_lista, name='excluir_lista'),
    path('enviar_lista/', views.enviar_lista, name='enviar_lista'),
]