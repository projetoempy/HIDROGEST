from django.urls import path
from .views import cadastrar_produto

urlpatterns = [
    path('cadastrar/<int:fornecedor_id>/', cadastrar_produto, name='cadastrar_produto'),
    path('cadastrar/<int:fornecedor_id>/', cadastrar_produto, name='cadastrar_produto'),

]