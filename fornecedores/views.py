from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.contrib.auth.decorators import login_required

from .models import Fornecedor
from django.contrib import messages

@login_required(login_url='/login/')
def lista_fornecedores(request):
    fornecedores = Fornecedor.objects.all()
    return render(request, 'fornecedores/fornecedores.html', {
        'fornecedores': fornecedores,
        'header_title': 'Fornecedores'
    })

@login_required(login_url='/login/')
def cadastrar_fornecedor(request):
    if request.method == "POST":
        nome = request.POST['nome']
        cnpj = request.POST['cnpj']
        email = request.POST['email']
        telefone = request.POST['telefone']
        endereco = request.POST['endereco']
        site = request.POST.get('site', None)
        fornecedor, created = Fornecedor.objects.get_or_create(
            cnpj=cnpj,
            defaults={
                'nome': nome,
                'email': email,
                'telefone': telefone,
                'endereco': endereco,
                'site': site,
            }
        )

        if not created:
            messages.error(request, f"Não é possível cadastrar fornecedor com CNPJ {cnpj} já existente.")
        else:
            messages.success(request, "Fornecedor cadastrado com sucesso!")
        return redirect('lista_fornecedores')
    return render(request, 'fornecedores/cadastro_fornecedor.html', {
        'header_title': 'Cadastrar Fornecedor',
    })

@login_required(login_url='/login/')
def editar_fornecedor(request, id):
    fornecedor = get_object_or_404(Fornecedor, id=id)
    if request.method == "POST":
        fornecedor.nome = request.POST['nome']
        fornecedor.cnpj = request.POST['cnpj']
        fornecedor.email = request.POST['email']
        fornecedor.telefone = request.POST['telefone']
        fornecedor.endereco = request.POST['endereco']
        fornecedor.site = request.POST.get('site', None)
        fornecedor.save()
        messages.success(request, "Fornecedor atualizado com sucesso!")
        return redirect('lista_fornecedores')
    return render(request, 'fornecedores/cadastro_fornecedor.html', {
        'fornecedor': fornecedor,
        'header_title': 'Editar Fornecedor'
    })

@login_required(login_url='/login/')
def excluir_fornecedor(request, id):
    fornecedor = get_object_or_404(Fornecedor, id=id)
    fornecedor.delete()
    messages.success(request, "Fornecedor excluído com sucesso!")
    return redirect('lista_fornecedores')