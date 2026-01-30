from django.urls import path
from . import views

urlpatterns = [
    path('empresas/', views.lista_empresas, name='lista_empresas'),
    path('empresas/nova/', views.cadastrar_empresa, name='cadastrar_empresa'),
    path('empresas/<int:id>/editar/', views.editar_empresa, name='editar_empresa'),
    path('empresas/<int:id>/excluir/', views.excluir_empresa, name='excluir_empresa'),
]