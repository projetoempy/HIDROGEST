from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.

from .models import Estoque, LogRetirada

from django.contrib import messages

from empresas.models import Empresa
from produtos.models import Produto

def lista_estoques(request):
    estoques = Estoque.objects.all()
    return render(request, 'estoques/estoques.html', {'estoques': estoques})

def adicionar_estoque(request):
    empresas = Empresa.objects.all()
    produtos = Produto.objects.all()
    empresa = request.user.empresa
    if request.method == "POST":
        empresa_id = request.POST['empresa']
        produto_id = request.POST['produto']
        quantidade = request.POST['quantidade']
        quantidade_minima = request.POST['quantidade_minima']
        empresa = Empresa.objects.get(id=empresa_id)
        produto = Produto.objects.get(id=produto_id)
        Estoque.objects.create(empresa=empresa, produto=produto, quantidade=quantidade, quantidade_minima=quantidade_minima)
        messages.success(request, "Produto adicionado ao estoque com sucesso!")
        return redirect('lista_estoques')
    return render(request, 'estoques/cadastro_estoque.html', {'empresas': empresas, 'produtos': produtos, 'empresa': empresa})

def editar_estoque(request, id):
    estoque = get_object_or_404(Estoque, id=id)
    empresas = Empresa.objects.all()
    produtos = Produto.objects.all()
    if request.method == "POST":
        estoque.empresa = Empresa.objects.get(id=request.POST['empresa'])
        estoque.produto = Produto.objects.get(id=request.POST['produto'])
        estoque.quantidade = request.POST['quantidade']
        estoque.quantidade_minima = request.POST['quantidade_minima']
        estoque.save()
        messages.success(request, "Estoque atualizado com sucesso!")
        return redirect('lista_estoques')
    return render(request, 'estoques/cadastro_estoque.html', {'estoque': estoque, 'empresas': empresas, 'produtos': produtos})

def excluir_estoque(request, id):
    estoque = get_object_or_404(Estoque, id=id)
    estoque.delete()
    messages.success(request, "Estoque excluído com sucesso!")
    return redirect('lista_estoques')

def log_retiradas(request):
    logs = LogRetirada.objects.all()
    return render(request, 'estoques/logs.html', {'logs': logs})