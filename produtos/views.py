from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.

from .forms import ProdutoForm
from fornecedores.models import Fornecedor
from django.contrib.auth.decorators import login_required
from .models import Produto
from .forms import ProdutoForm

@login_required
def cadastrar_produto(request, fornecedor_id):
    fornecedor = get_object_or_404(Fornecedor, id=fornecedor_id)
    produtos_do_fornecedor = Produto.objects.filter(fornecedor=fornecedor)

    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            produto = form.save(commit=False)
            produto.fornecedor = fornecedor
            produto.save()
            return redirect('cadastrar_produto', fornecedor_id=fornecedor.id)

    else:
        form = ProdutoForm()

    return render(request, 'produtos/cadastro_produto.html', {
        'form': form,
        'fornecedor': fornecedor,
        'produtos': produtos_do_fornecedor
    })


@login_required
def editar_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            return redirect('cadastrar_produto', fornecedor_id=produto.fornecedor.id)
    else:
        form = ProdutoForm(instance=produto)
    return render(request, 'produtos/editar_produto.html', {'form': form, 'produto': produto})

@login_required
def excluir_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    fornecedor_id = produto.fornecedor.id
    produto.delete()
    return redirect('cadastrar_produto', fornecedor_id=fornecedor_id)
