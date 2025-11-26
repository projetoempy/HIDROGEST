from django.shortcuts import render, redirect

from usuarios.models import Usuario
from django.contrib.auth import authenticate, login, logout
from .forms import CadastroFuncionarioForm
from .models import Usuario
from estoque.models import Estoque
from django.contrib.auth.decorators import login_required
from compras.models import ListaCompra, ItemCompra
from django.db import models
from retiradas.models import Retirada
from fornecedores.models import Fornecedor

# Página inicial
def home(request):
    # Atualiza os dados de estoque com base nos produtos
    produtos_estoque = Estoque.objects.all()
    return render(request, 'home.html', {'produtos_estoque': produtos_estoque})

# Login
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

# Logout
def logout_view(request):
    logout(request)
    return redirect('home')

# Cadastro de funcionário
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

# Página de sucesso após cadastro
def cadastro_sucesso(request):
    return render(request, 'usuarios/cadastro_sucesso.html')

# Dashboard do gerente
@login_required
def dashboard_gerente(request):
    if request.user.tipo != 'gerente':
        return redirect('home')
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id')
        if usuario_id:
            usuario = Usuario.objects.filter(id=usuario_id).first()
            if usuario:
                usuario.status_ativo = True
                usuario.save()

    # Dados para o dashboard
    total_produtos = Estoque.objects.count()
    produtos_criticos = Estoque.objects.filter(quantidade__lt=models.F('quantidade_minima'))
    total_listas = ListaCompra.objects.count()
    total_itens_comprados = ItemCompra.objects.aggregate(total=models.Sum('quantidade_desejada'))['total']
    pendentes = Usuario.objects.filter(status_ativo=False, tipo='funcionario')
    logs = Retirada.objects.select_related('produto', 'funcionario').order_by('-data_hora')
    fornecedores = Fornecedor.objects.all()
    produtos_estoque = Estoque.objects.select_related('produto').all()

    contexto = {
        'total_produtos': total_produtos,
        'produtos_criticos': produtos_criticos,
        'total_listas': total_listas,
        'total_itens_comprados': total_itens_comprados,
        'pendentes': pendentes,
        'logs': logs,
        'fornecedores': fornecedores,
        'produtos_estoque': produtos_estoque,
    }

    return render(request, 'usuarios/dashboard_gerente.html', contexto)

# Ativação de usuários pendentes
@login_required
def ativar_usuarios(request):
    if request.user.tipo != 'gerente':
        return redirect('home')

    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id')
        usuario = Usuario.objects.get(id=usuario_id)
        usuario.status_ativo = True
        usuario.save()

    pendentes = Usuario.objects.filter(status_ativo=False, tipo='funcionario')
    return render(request, 'usuarios/ativar_usuarios.html', {'pendentes': pendentes})