from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.

from django.contrib import messages
from .models import Produto
from fornecedores.models import Fornecedor

def lista_produtos(request):
    produtos = Produto.objects.all()
    return render(request, 'produtos/produtos.html', {'produtos': produtos})

def cadastrar_produto(request):
    fornecedores = Fornecedor.objects.all()
    if request.method == "POST":
        nome = request.POST['nome']
        fornecedor_id = request.POST['fornecedor']
        preco = request.POST['preco']
        descricao = request.POST.get('descricao', None)
        fornecedor = Fornecedor.objects.get(id=fornecedor_id)
        Produto.objects.create(nome=nome, fornecedor=fornecedor, preco=preco, descricao=descricao)
        messages.success(request, "Produto cadastrado com sucesso!")
        return redirect('lista_produtos')
    return render(request, 'produtos/cadastro_produto.html', {'fornecedores': fornecedores})

def editar_produto(request, id):
    produto = get_object_or_404(Produto, id=id)
    fornecedores = Fornecedor.objects.all()
    if request.method == "POST":
        produto.nome = request.POST['nome']
        fornecedor_id = request.POST['fornecedor']
        produto.fornecedor = Fornecedor.objects.get(id=fornecedor_id)
        produto.preco = request.POST['preco']
        produto.descricao = request.POST.get('descricao', None)
        produto.save()
        messages.success(request, "Produto atualizado com sucesso!")
        return redirect('lista_produtos')
    return render(request, 'produtos/cadastro_produto.html', {'produto': produto, 'fornecedores': fornecedores})

def excluir_produto(request, id):
    produto = get_object_or_404(Produto, id=id)
    produto.delete()
    messages.success(request, "Produto excluído com sucesso!")
    return redirect('lista_produtos')