from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.

from django.contrib.auth import authenticate, login, logout
from .models import Usuario
from empresas.models import Empresa
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from estoques.models import Estoque, LogRetirada
from produtos.models import Produto
from django.utils.dateparse import parse_date

#from django.contrib.auth.forms import UserCreationForm


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.status_ativo:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Usuário ou senha inválidos, ou conta inativa.")
    return render(request, 'usuarios/login.html', {
        'header_title': 'Login'
    })

@login_required(login_url='/login/')
def dashboard_view(request):
    usuario = request.user
    empresa_usuario = usuario.empresa

    # pega apenas estoques da empresa do usuário logado
    estoque = Estoque.objects.filter(empresa=empresa_usuario)

    # Produtos para o filtro
    produtos = Produto.objects.all()

    # Saídas feitas pelo usuário logado 
    retiradas = LogRetirada.objects.filter(empresa=empresa_usuario).order_by('-data_hora')

    if request.method == "GET":
        produto_nome = request.GET.get('produto')
        data_inicio = request.GET.get('data_inicio')
        data_fim = request.GET.get('data_fim')

        if produto_nome:
            retiradas = retiradas.filter(produto__nome__icontains=produto_nome)
        if data_inicio:
            retiradas = retiradas.filter(data_hora__date__gte=parse_date(data_inicio))
        if data_fim:
            retiradas = retiradas.filter(data_hora__date__lte=parse_date(data_fim))

    return render(request, 'usuarios/dashboard.html', {
        'user': usuario,
        'estoque': estoque,
        'empresa_usuario': empresa_usuario,
        'retiradas': retiradas,
        'produtos': produtos,
        'header_title': 'Dashboard',
    })


def logout_view(request):
    logout(request)
    return redirect('login')

def cadastro_usuario(request):
    empresas = Empresa.objects.all()
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        empresa_id = request.POST['empresa']

        if password1 != password2:
            messages.error(request, "As senhas não coincidem.")
        else:
            empresa = Empresa.objects.get(id=empresa_id)
            usuario = Usuario.objects.create_user(
                username=username,
                email=email,
                password=password1,
                empresa=empresa,
                status_ativo=False  # conta começa inativa
            )
            messages.success(request, "Usuário cadastrado com sucesso! Aguarde ativação.")
            return redirect('login')

    return render(request, 'usuarios/cadastro.html', {
        'empresas': empresas,
        'header_title': 'Cadastrar Usuário'
    })

@login_required(login_url='/login/')
def lista_usuarios(request):
    usuarios = Usuario.objects.all()
    tipos_usuario = Usuario.TIPOS_USUARIO
    empresas = Empresa.objects.all()
    return render(request, 'usuarios/lista_usuarios.html', {
        'usuarios': usuarios, 
        'tipos_usuario': tipos_usuario,
        'empresas': empresas,
        'header_title': 'Usuários'
    })

@login_required(login_url='/login/')
def alterar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    if request.method == "POST":
        novo_tipo = request.POST.get('tipo_usuario')
        empresa_id = request.POST.get('empresa_id')
        empresa = Empresa.objects.get(id=empresa_id) if empresa_id else None

        # regra: impedir filial em empresa que já tem matriz
        if novo_tipo in ["GERENTE_FILIAL", "GESTOR_FILIAL"]:
            existe_matriz = Usuario.objects.filter(
                empresa=empresa,
                tipo_usuario__in=["GERENTE_MATRIZ", "GESTOR_MATRIZ"]
            ).exclude(id=usuario.id).exists()

            if existe_matriz:
                messages.error(request, f"A empresa {empresa.nome} já possui usuário do tipo Matriz. \
Não é permitido cadastrar usuários do tipo Filial nessa empresa.")
                return redirect('lista_usuarios')

        # regra: impedir matriz em empresa diferente da já existente
        if novo_tipo in ["GERENTE_MATRIZ", "GESTOR_MATRIZ"]:
            matriz_existente = Usuario.objects.filter(
                tipo_usuario__in=["GERENTE_MATRIZ", "GESTOR_MATRIZ"]
            ).exclude(id=usuario.id).first()

            if matriz_existente and matriz_existente.empresa != empresa:
                messages.error(request, f"Já existe um usuário matriz na empresa {matriz_existente.empresa.nome}. \
Novos usuários do tipo matriz só podem ser cadastrados nessa mesma empresa.")
                return redirect('lista_usuarios')

        # se passou nas regras, atualiza normalmente
        usuario.tipo_usuario = novo_tipo if novo_tipo else None
        usuario.empresa = empresa
        usuario.save()

        messages.success(request, f"Usuário {usuario.username} atualizado com sucesso.")
    return redirect('lista_usuarios')

@login_required(login_url='/login/')
def toggle_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    usuario.status_ativo = not usuario.status_ativo
    usuario.save()
    status = "ativado" if usuario.status_ativo else "desativado"
    messages.success(request, f"Usuário {status} com sucesso.")
    return redirect('lista_usuarios')