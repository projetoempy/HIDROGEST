from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cadastro/', views.cadastro_usuario, name='cadastro_usuario'),
    path('', views.dashboard_view, name='dashboard'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('lista_usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/<int:id>/alterar-tipo/', views.alterar_usuario, name='alterar_usuario'),
    path('usuarios/<int:id>/toggle/', views.toggle_usuario, name='toggle_usuario'),
]