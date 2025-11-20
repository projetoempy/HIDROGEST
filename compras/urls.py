from django.urls import path
from .views import lista_compras_view, produtos_por_fornecedor

urlpatterns = [
    path('', lista_compras_view, name='lista_compras'),
    path('produtos/<int:fornecedor_id>/', produtos_por_fornecedor, name='produtos_por_fornecedor'),
]