from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.

from .models import ListaCompra, ItemListaCompra, LogAlteracaoLista
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from produtos.models import Produto
from fornecedores.models import Fornecedor
from django.utils import timezone


@login_required(login_url='/login/')
def lista_compras(request):
    if request.user.tipo_usuario in ["GERENTE_MATRIZ", "GESTOR_MATRIZ"]:
        # gerentes matriz/gestor matriz veem todas menos as em análise e em processo de autorização
        listas = ListaCompra.objects.exclude(
            status__in=["EM_ANALISE", "EM_PROCESSO_AUTORIZACAO"]
        ) | ListaCompra.objects.filter(
            empresa=request.user.empresa,
            status__in=["EM_ANALISE", "EM_PROCESSO_AUTORIZACAO"]
        )
    else:
        # Outros só veem listas da própria empresa
        listas = ListaCompra.objects.filter(empresa=request.user.empresa)

    return render(request, 'compras/listas.html', {'listas': listas})


@login_required(login_url='/login/')
def criar_lista(request):
    empresa = request.user.empresa

    if request.method == "POST":
        # gera número automático
        ultimo = ListaCompra.objects.filter(empresa=empresa).order_by('id').last()
        if ultimo:
            numero_seq = int(ultimo.numero.split('/')[0]) + 1
        else:
            numero_seq = 1
        numero = f"{str(numero_seq).zfill(5)}/{timezone.now().year}"

        lista = ListaCompra.objects.create(
            numero=numero,
            empresa=empresa,
            criado_por=request.user,
            status='EM_ANALISE'
        )

        # percorre todos os produtos enviados
        for produto in Produto.objects.all():
            qtd = int(request.POST.get(f"produto_{produto.id}", 0))
            if qtd > 0:
                ItemListaCompra.objects.create(
                    lista=lista,
                    produto=produto,
                    quantidade_desejada=qtd
                )

        messages.success(request, f"Lista {lista.numero} criada com sucesso!")
        return redirect('lista_compras')

    # GET → renderiza formulário com fornecedores e produtos
    fornecedores = Fornecedor.objects.all().prefetch_related('produtos')
    return render(request, 'compras/cadastro_lista.html', {
        'empresa': empresa,
        'fornecedores': fornecedores
    })


def registrar_log(lista, produto, usuario, antiga, nova):
    """Função utilitária para registrar alterações no log."""
    LogAlteracaoLista.objects.create(
        lista=lista,
        produto=produto,
        alterado_por=usuario,
        quantidade_antiga=antiga,
        quantidade_nova=nova,
        data_hora=timezone.now()
    )


@login_required(login_url='/login/')
def detalhes_lista(request, id):
    lista = get_object_or_404(ListaCompra, id=id)
    itens = ItemListaCompra.objects.filter(lista=lista)
    alteracoes = LogAlteracaoLista.objects.filter(lista=lista)
    fornecedores = Fornecedor.objects.all().prefetch_related('produtos')

    # calcular preço total de cada item e valor total da lista
    itens_com_preco = []
    for item in itens:
        preco_unitario = item.produto.preco
        preco_total = item.quantidade_desejada * preco_unitario
        itens_com_preco.append({
            'obj': item,
            'preco_unitario': preco_unitario,
            'preco_total': preco_total
        })

    total_lista = sum(i['preco_total'] for i in itens_com_preco)

    if request.method == "POST":
         # Botão Solicitar Autorização
        if "solicitar_autorizacao" in request.POST:
            lista.status = "EM_PROCESSO_AUTORIZACAO"
            lista.save()
            messages.success(request, "Solicitação de autorização enviada!")
            return redirect('detalhes_lista', id=lista.id)

        # Botão Autorizar
        if "AUTORIZADA" in request.POST:
            lista.status = "AUTORIZADA"
            lista.save()
            messages.success(request, "Lista autorizada com sucesso!")
            return redirect('detalhes_lista', id=lista.id)

        # Adicionar novos produtos
        for fornecedor in fornecedores:
            for produto in fornecedor.produtos.all():
                qtd = int(request.POST.get(f"produto_{produto.id}", 0))
                if qtd > 0:
                    item_existente = ItemListaCompra.objects.filter(lista=lista, produto=produto).first()
                    if item_existente:
                        messages.warning(request, f"O produto {produto.nome} já está na lista e não pode ser duplicado.")
                    else:
                        ItemListaCompra.objects.create(
                            lista=lista,
                            produto=produto,
                            quantidade_desejada=qtd
                        )
                        registrar_log(lista, produto, request.user, 0, qtd)
                        messages.success(request, f"Produto {produto.nome} adicionado à lista.")

        # Atualizar ou excluir itens existentes
        for item in itens:
            nova_qtd = int(request.POST.get(f"item_{item.id}", item.quantidade_desejada))

            if nova_qtd == 0:
                registrar_log(lista, item.produto, request.user, item.quantidade_desejada, 0)
                item.delete()
                messages.info(request, f"Produto {item.produto.nome} removido da lista.")
            elif nova_qtd != item.quantidade_desejada:
                registrar_log(lista, item.produto, request.user, item.quantidade_desejada, nova_qtd)
                item.quantidade_desejada = nova_qtd
                item.save()

        return redirect('detalhes_lista', id=lista.id)

    return render(request, 'compras/detalhes.html', {
        'lista': lista,
        'itens': itens_com_preco,   # recebe itens com preço
        'alteracoes': alteracoes,
        'fornecedores': fornecedores,
        'total_lista': total_lista,
    })


@login_required(login_url='/login/')
def excluir_lista(request, id):
    lista = get_object_or_404(ListaCompra, id=id)
    lista.delete()
    messages.success(request, "Lista excluída com sucesso!")
    return redirect('lista_compras')
