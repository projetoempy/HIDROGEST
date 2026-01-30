from django.shortcuts import render, redirect, get_object_or_404
from .models import Empresa
# Create your views here.

from django.contrib import messages

def lista_empresas(request):
    empresas = Empresa.objects.all()
    return render(request, 'empresas/empresas.html', {
        'empresas': empresas,
        'header_title': 'Empresas'
    })

def cadastrar_empresa(request):
    if request.method == "POST":
        nome = request.POST['nome']
        email = request.POST['email']
        telefone = request.POST['telefone']
        endereco = request.POST['endereco']
        Empresa.objects.create(nome=nome, email=email, telefone=telefone, endereco=endereco)
        messages.success(request, "Empresa cadastrada com sucesso!")
        return redirect('lista_empresas')
    return render(request, 'empresas/cadastro_empresa.html', {
        'header_title': 'Cadastrar Empresa'
    })

def editar_empresa(request, id):
    empresa = get_object_or_404(Empresa, id=id)
    if request.method == "POST":
        empresa.nome = request.POST['nome']
        empresa.email = request.POST['email']
        empresa.telefone = request.POST['telefone']
        empresa.endereco = request.POST['endereco']
        empresa.save()
        messages.success(request, "Empresa atualizada com sucesso!")
        return redirect('lista_empresas')
    return render(request, 'empresas/cadastro_empresa.html', {
        'empresa': empresa,
        'header_title': 'Editar Empresa'
        })

def excluir_empresa(request, id):
    empresa = get_object_or_404(Empresa, id=id)
    empresa.delete()
    messages.success(request, "Empresa excluída com sucesso!")
    return redirect('lista_empresas')