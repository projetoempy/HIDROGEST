from django.urls import path
from . import views
from .views import dashboard_funcionario


urlpatterns = [
    path('funcionario/retirar/<int:produto_id>/', views.retirar_produto, name='retirar_produto'),
    path('funcionario/dashboard/', dashboard_funcionario, name='dashboard_funcionario'),
]