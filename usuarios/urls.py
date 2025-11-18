from django.urls import path
from .views import home, login_view, logout_view, cadastro_funcionario, cadastro_sucesso,dashboard_gerente, ativar_usuarios

urlpatterns = [
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('cadastro/funcionario/', cadastro_funcionario, name='cadastro_funcionario'),
    path('cadastro/sucesso/', cadastro_sucesso, name='cadastro_sucesso'),
    path('dashboard/gerente/', dashboard_gerente, name='dashboard_gerente'),
    path('ativar/usuarios/', ativar_usuarios, name='ativar_usuarios'),
]
