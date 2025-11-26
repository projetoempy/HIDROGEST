from django.shortcuts import render, redirect
from .models import ListaCompra, ItemCompra
from produtos.models import Produto
from fornecedores.models import Fornecedor
from estoque.models import Estoque
from usuarios.views import login_required

@login_required
def lista_compras_view(request):
    erro = None  # variável para armazenar mensagem de erro

    if request.method == 'POST':
        # Processa o recebimento dos itens
        if 'receber_lista_id' in request.POST:
            lista_id = request.POST.get('receber_lista_id')
            lista = ListaCompra.objects.get(id=lista_id)

            if not lista.recebido:
                itens = ItemCompra.objects.filter(lista=lista)
                for item in itens:
                    produto = item.produto
                    estoque, criado = Estoque.objects.get_or_create(
                        produto=produto,
                        defaults={'quantidade': 0, 'quantidade_minima': 0}
                    )
                    estoque.quantidade += item.quantidade_desejada
                    estoque.save()
                lista.recebido = True
                lista.save()

            return redirect('lista_compras')


        # Criação de nova lista de compras
        fornecedor_id = request.POST.get('fornecedor_id')
        if not fornecedor_id:
            erro = 'Você precisa selecionar um fornecedor antes de criar a lista.'

            # Recarrega os dados necessários para o template
            listas = ListaCompra.objects.select_related('fornecedor').order_by('-data_criacao')
            itens_por_lista = ItemCompra.objects.select_related('produto').all()
            itens_agrupados = {}
            for item in itens_por_lista:
                itens_agrupados.setdefault(item.lista_id, []).append(item)
            for lista in listas:
                lista.itens = itens_agrupados.get(lista.id, [])

            fornecedores = Fornecedor.objects.all()
            produtos = Produto.objects.all()

            return render(request, 'compras/compras_lista.html', {
                'listas': listas,
                'fornecedores': fornecedores,
                'produtos': produtos,
                'erro': erro,
            })

        fornecedor = Fornecedor.objects.get(id=fornecedor_id)
        nova_lista = ListaCompra.objects.create(fornecedor=fornecedor)

        produto_ids = request.POST.getlist('produto_ids')
        itens_validos = False

        for produto_id in produto_ids:
            quantidade = request.POST.get(f'quantidade_{produto_id}')
            if quantidade and quantidade.isdigit() and int(quantidade) > 0:
                produto = Produto.objects.get(id=produto_id)
                ItemCompra.objects.create(
                    lista=nova_lista,
                    produto=produto,
                    quantidade_desejada=int(quantidade),
                    valor_total=0
                )
                itens_validos = True

        if not itens_validos:
            nova_lista.delete()
            erro = 'Nenhum item válido foi selecionado para este fornecedor.'
        else:
            return redirect('lista_compras')

    # GET ou POST com erro: exibe listas existentes com seus itens
    listas = ListaCompra.objects.select_related('fornecedor').order_by('-data_criacao')
    itens_por_lista = ItemCompra.objects.select_related('produto').all()

    # Agrupa os itens por lista
    itens_agrupados = {}
    for item in itens_por_lista:
        itens_agrupados.setdefault(item.lista_id, []).append(item)

    # Anexa os itens a cada lista
    for lista in listas:
        lista.itens = itens_agrupados.get(lista.id, [])

    fornecedores = Fornecedor.objects.all()
    produtos = Produto.objects.all()

    return render(request, 'compras/compras_lista.html', {
        'listas': listas,
        'fornecedores': fornecedores,
        'produtos': produtos,
        'erro': erro,
    })


def produtos_por_fornecedor(request, fornecedor_id):
    produtos = Produto.objects.filter(fornecedor_id=fornecedor_id)
    return render(request, 'compras/produtos_por_fornecedor.html', {
        'produtos': produtos
    })