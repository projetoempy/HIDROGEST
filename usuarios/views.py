from django.shortcuts import render, redirect

# Create your views here.

from django.contrib.auth import authenticate, login, logout
from .forms import CadastroFuncionarioForm
from .models import Usuario
from estoque.models import Estoque

def home(request):
    produtos_estoque = Estoque.objects.select_related('produto').all()
    return render(request, 'usuarios/home.html', {'produtos_estoque': produtos_estoque})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        usuario = authenticate(request, username=username, password=password)
        if usuario is not None and usuario.status_ativo:
            login(request, usuario)
            if usuario.tipo == 'gerente':
                return redirect('dashboard_gerente')
            elif usuario.tipo == 'funcionario':
                return redirect('dashboard_funcionario')
        else:
            erro = "Credenciais inválidas ou conta inativa."
            return render(request, 'usuarios/login.html', {'erro': erro})
    return render(request, 'usuarios/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def cadastro_funcionario(request):
    if request.method == 'POST':
        form = CadastroFuncionarioForm(request.POST)
        if form.is_valid():
            funcionario = form.save(commit=False)
            funcionario.tipo = 'funcionario'
            funcionario.status_ativo = False
            funcionario.set_password(form.cleaned_data['password'])
            funcionario.save()
            return redirect('cadastro_sucesso')
    else:
        form = CadastroFuncionarioForm()
    return render(request, 'usuarios/cadastro_funcionario.html', {'form': form})