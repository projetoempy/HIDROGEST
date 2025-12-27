from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.

from .models import ListaCompra, ItemListaCompra, LogAlteracaoLista
from django.contrib.auth.decorators import login_required
from django.contrib import messages
#from empresas.models import Empresa
from produtos.models import Produto
from fornecedores.models import Fornecedor
from django.utils import timezone
#from django.http import HttpResponseForbidden


@login_required(login_url='/login/')
def lista_compras(request):
    if request.user.tipo_usuario in ["GERENTE_MATRIZ", "GESTOR_MATRIZ"]:
        # admin vê todas
        listas = ListaCompra.objects.all()
    else:
        # funcionário só vê:
        # - listas da própria empresa com status EM_ANALISE
        listas = ListaCompra.objects.filter(
            empresa=request.user.empresa)

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


@login_required(login_url='/login/')
def editar_lista(request, id):
    # só permite se for gerente
    if request.user.tipo_usuario not in ["GERENTE_MATRIZ", "GERENTE_FILIAL"]:
        messages.error(request, "Você não tem permissão para editar esta lista.")
        return redirect('lista_compras')
        #return HttpResponseForbidden("Você não tem permissão para editar esta lista.")
    lista = get_object_or_404(ListaCompra, id=id)
    itens = ItemListaCompra.objects.filter(lista=lista)

    if request.method == "POST":
        # Atualiza status
        lista.status = request.POST.get('status', lista.status)
        lista.save()

        # Atualiza quantidades dos itens
        for item in itens:
            nova_qtd = int(request.POST.get(f"item_{item.id}", item.quantidade_desejada))
            if nova_qtd != item.quantidade_desejada:
                # salva log da alteração
                LogAlteracaoLista.objects.create(
                    lista=lista,
                    produto=item.produto,
                    alterado_por=request.user,
                    quantidade_antiga=item.quantidade_desejada,
                    quantidade_nova=nova_qtd,
                    data_hora=timezone.now()
                )
                # atualiza item
                item.quantidade_desejada = nova_qtd
                item.save()

        messages.success(request, "Lista atualizada com sucesso!")
        return redirect('detalhes_lista', id=lista.id)

    return render(request, 'compras/editar_lista.html', {
        'lista': lista,
        'itens': itens
    })

@login_required(login_url='/login/')
def detalhes_lista(request, id):
    lista = get_object_or_404(ListaCompra, id=id)

    # Restrição: se a lista está em análise e o usuário não é da mesma empresa
    if lista.status == "EM_ANALISE" and lista.empresa != request.user.empresa:
        messages.error(request, "Você não tem permissão para visualizar esta lista.")
        return redirect('lista_compras')
        #return HttpResponseForbidden("Você não tem permissão para visualizar esta lista.")

    itens = ItemListaCompra.objects.filter(lista=lista)
    alteracoes = LogAlteracaoLista.objects.filter(lista=lista)

    if request.method == "POST":
        if "solicitar_autorizacao" in request.POST:
            lista.status = "EM_PROCESSO_AUTORIZACAO"
            lista.save()
            messages.success(request, "Solicitação de autorização enviada!")
            return redirect('detalhes_lista', id=lista.id)

        # fluxo normal de salvar alterações

        for item in itens:
            nova_qtd = int(request.POST.get(f"item_{item.id}", item.quantidade_desejada))
            if nova_qtd != item.quantidade_desejada:
                LogAlteracaoLista.objects.create(
                    lista=lista,
                    produto=item.produto,
                    alterado_por=request.user,
                    quantidade_antiga=item.quantidade_desejada,
                    quantidade_nova=nova_qtd,
                    data_hora=timezone.now()
                )
                item.quantidade_desejada = nova_qtd
                item.save()
        messages.success(request, "Itens atualizados com sucesso!")
        return redirect('detalhes_lista', id=lista.id)

    return render(request, 'compras/detalhes.html', {
        'lista': lista,
        'itens': itens,
        'alteracoes': alteracoes
    })

@login_required(login_url='/login/')
def excluir_lista(request, id):
    lista = get_object_or_404(ListaCompra, id=id)
    lista.delete()
    messages.success(request, "Lista excluída com sucesso!")
    return redirect('lista_compras')


@login_required(login_url='/login/')
def adicionar_item(request, lista_id):
    lista = get_object_or_404(ListaCompra, id=lista_id)
    produtos = Produto.objects.all()
    if request.method == "POST":
        produto_id = request.POST['produto']
        quantidade_desejada = request.POST['quantidade_desejada']
        produto = Produto.objects.get(id=produto_id)
        ItemListaCompra.objects.create(lista=lista, produto=produto, quantidade_desejada=quantidade_desejada)
        messages.success(request, "Item adicionado à lista com sucesso!")
        return redirect('detalhes_lista', id=lista.id)
    return render(request, 'compras/adicionar_item.html', {'lista': lista, 'produtos': produtos})