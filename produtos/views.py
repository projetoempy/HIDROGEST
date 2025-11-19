from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.

from .forms import ProdutoForm
from fornecedores.models import Fornecedor
from django.contrib.auth.decorators import login_required

@login_required
def cadastrar_produto(request, fornecedor_id):
    fornecedor = get_object_or_404(Fornecedor, id=fornecedor_id)

    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            produto = form.save(commit=False)
            produto.fornecedor = fornecedor
            produto.save()
            return redirect('dashboard_gerente')
    else:
        form = ProdutoForm()

    return render(request, 'produtos/cadastro_produto.html', {
        'form': form,
        'fornecedor': fornecedor
    })