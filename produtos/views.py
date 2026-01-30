from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.

from django.contrib import messages
from .models import Produto
from fornecedores.models import Fornecedor
from django.contrib.auth.decorators import login_required

@login_required(login_url='/login/')
def lista_produtos(request):
    filtro_nome = request.GET.get('produto_nome', '')

    fornecedores = Fornecedor.objects.all().prefetch_related('produtos')

    # aplica filtro nos produtos de cada fornecedor
    for fornecedor in fornecedores:
        if filtro_nome:
            fornecedor.produtos_filtrados = fornecedor.produtos.filter(nome__icontains=filtro_nome)
        else:
            fornecedor.produtos_filtrados = fornecedor.produtos.all()

    return render(request, 'produtos/produtos_fornecedor.html', {
        'fornecedores': fornecedores,
        'filtro_nome': filtro_nome,
        'header_title': 'Fornecedores e Produtos',
    })

@login_required(login_url='/login/')
def cadastrar_produto(request, fornecedor_id=None):
    fornecedores = Fornecedor.objects.all()
    fornecedor = None

    if fornecedor_id:
        fornecedor = get_object_or_404(Fornecedor, id=fornecedor_id)

    if request.method == "POST":
        nome = request.POST['nome']
        preco = request.POST['preco']
        descricao = request.POST.get('descricao', '')
        imagem = request.FILES.get("imagem")

        if fornecedor:
            fornecedor_final = fornecedor
        else:
            fornecedor_final = get_object_or_404(Fornecedor, id=request.POST['fornecedor'])

        Produto.objects.create(
            fornecedor=fornecedor_final,
            nome=nome,
            preco=preco,
            descricao=descricao,
            imagem=imagem,
        )
        messages.success(request, f"Produto cadastrado para o fornecedor {fornecedor_final.nome}!")
        return redirect('lista_produtos')

    return render(request, 'produtos/cadastro_produto.html', {
        'fornecedor': fornecedor,
        'fornecedores': fornecedores,
        'header_title': 'Cadastrar Produto',
    })
@login_required(login_url='/login/')
def editar_produto(request, id):
    produto = get_object_or_404(Produto, id=id)
    fornecedores = Fornecedor.objects.all()
    if request.method == "POST":
        produto.nome = request.POST['nome']
        fornecedor_id = request.POST['fornecedor']
        produto.fornecedor = Fornecedor.objects.get(id=fornecedor_id)
        produto.preco = request.POST['preco']
        produto.descricao = request.POST.get('descricao', None)
        
        if 'imagem' in request.FILES:
            produto.imagem = request.FILES['imagem']

        produto.save()
        messages.success(request, "Produto atualizado com sucesso!")
        return redirect('lista_produtos')
    return render(request, 'produtos/cadastro_produto.html', {
        'produto': produto, 
        'fornecedores': fornecedores,
        'header_title': 'Editar Produto',
    })

@login_required(login_url='/login/')
def excluir_produto(request, id):
    produto = get_object_or_404(Produto, id=id)
    produto.delete()
    messages.success(request, "Produto excluído com sucesso!")
    return redirect('lista_produtos')