from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.

from .models import ListaCompra, ItemListaCompra, LogAlteracaoLista

from django.contrib import messages
from empresas.models import Empresa
from produtos.models import Produto


def lista_compras(request):
    listas = ListaCompra.objects.all()
    return render(request, 'compras/listas.html', {'listas': listas})

from django.utils import timezone

def criar_lista(request):
    empresa = request.user.empresa  # pega empresa do usuário logado

    if request.method == "POST":
        # gera número automático
        ultimo = ListaCompra.objects.filter(empresa=empresa).order_by('id').last()
        if ultimo:
            numero_seq = int(ultimo.numero.split('/')[0]) + 1
        else:
            numero_seq = 1
        numero = f"{str(numero_seq).zfill(5)}/{timezone.now().year}"

        # cria lista com status fixo
        lista = ListaCompra.objects.create(
            numero=numero,
            empresa=empresa,
            criado_por=request.user,
            status='EM_ANALISE'
        )
        messages.success(request, f"Lista {lista.numero} criada com sucesso!")
        return redirect('lista_compras')

    # passa empresa para o template
    return render(request, 'compras/cadastro_lista.html', {'empresa': empresa})

#falta ajustar o método(verificar se o status da lista permite edição, caso permita verificar se há itens na lista e tornar os campos editáveis) (jailson)
def editar_lista(request, id):
    lista = get_object_or_404(ListaCompra, id=id)
    if request.method == "POST":
        lista.status = request.POST['status']
        lista.save()
        messages.success(request, "Lista atualizada com sucesso!")
        return redirect('lista_compras')
    return render(request, 'compras/cadastro_lista.html', {'lista': lista})

def detalhes_lista(request, id):
    lista = get_object_or_404(ListaCompra, id=id)
    itens = ItemListaCompra.objects.filter(lista=lista)
    alteracoes = LogAlteracaoLista.objects.filter(lista=lista)
    return render(request, 'compras/detalhes.html', {'lista': lista, 'itens': itens, 'alteracoes': alteracoes})

def excluir_lista(request, id):
    lista = get_object_or_404(ListaCompra, id=id)
    lista.delete()
    messages.success(request, "Lista excluída com sucesso!")
    return redirect('lista_compras')

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