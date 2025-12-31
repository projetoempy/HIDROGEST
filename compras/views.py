from urllib import request
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.

from .models import ListaCompra, ItemListaCompra, LogAlteracaoLista
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from produtos.models import Produto
from fornecedores.models import Fornecedor
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum
from estoques.models import Estoque, LogEntrada


@login_required(login_url='/login/')
def lista_compras(request):
    if request.user.tipo_usuario in ["GERENTE_MATRIZ", "GESTOR_MATRIZ"]:
        # gerentes matriz/gestor matriz veem todas menos as em análise e em processo de autorização
        listas = ListaCompra.objects.exclude(
            status__in=["EM_CRIACAO", "EM_PROCESSO_AUTORIZACAO"]
        ) | ListaCompra.objects.filter(
            empresa=request.user.empresa,
            status__in=["EM_CRIACAO", "EM_PROCESSO_AUTORIZACAO"]
        )
    else:
        # Outros só veem listas da própria empresa
        listas = ListaCompra.objects.filter(empresa=request.user.empresa)

     # Filtros
    empresa_nome = request.GET.get('empresa') or ''
    status = request.GET.get('status')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    if empresa_nome:
        listas = listas.filter(empresa__nome__icontains=empresa_nome)
    if status:
        listas = listas.filter(status=status)
    if data_inicio:
        listas = listas.filter(data_criacao__date__gte=data_inicio)
    if data_fim:
        listas = listas.filter(data_criacao__date__lte=data_fim)
    principal = request.GET.get('principal')  # pode ser "sim" ou vazio

    if principal == "unidas":
        # mantém apenas listas principais (as que possuem listas_unidas)
        listas = listas.filter(listas_unidas__isnull=False).distinct()


    # separa principais e unidas, serve para adicionar filtro de pesquisa
    principais = []
    unidas = []
    for lista in listas:
        if lista.listas_unidas.exists():
            lista.is_principal = True
            principais.append(lista)
        else:
            lista.is_principal = False
            unidas.append(lista)
    
    tem_autorizada = listas.filter(empresa=request.user.empresa, status="AUTORIZADA").exists()
    tem_unida = listas.filter(empresa=request.user.empresa, status="UNIDA").exists()
    tem_consolidada = listas.filter(empresa=request.user.empresa, status="CONSOLIDADA").exists()
    return render(request, 'compras/listas.html', {
        'listas': listas, 
        'tem_autorizada': tem_autorizada, 
        'tem_unida': tem_unida, 
        'tem_consolidada': tem_consolidada,
        'principais': principais, 
        'unidas': unidas,
        'empresa_nome': empresa_nome,
        'status': status,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
    })


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
            status='EM_CRIACAO'
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
        return redirect('detalhes_lista', id=lista.id)

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
            if request.user.tipo_usuario != "GESTOR_MATRIZ" and request.user.tipo_usuario != "GESTOR_FILIAL":
                messages.error(request, "Você não tem permissão para processar compras.")
                return redirect("lista_compras")
            lista.status = "EM_PROCESSO_AUTORIZACAO"
            lista.save()
            messages.success(request, "Solicitação de autorização enviada!")
            return redirect('lista_compras')

        # Botão Autorizar
        if "AUTORIZADA" in request.POST:
            if request.user.tipo_usuario != "GERENTE_MATRIZ" and request.user.tipo_usuario != "GERENTE_FILIAL":
                messages.error(request, "Você não tem permissão para autorizar compras.")
                return redirect("lista_compras")
            lista.status = "AUTORIZADA"
            lista.save()
            messages.success(request, "Lista autorizada com sucesso!")
            return redirect('lista_compras')

        # Botão Consolidar
        if "CONSOLIDADA" in request.POST:
            if request.user.tipo_usuario != "GERENTE_MATRIZ":
                messages.error(request, "Você não tem permissão para consolidar compras.")
                return redirect("lista_compras")
            lista.status = "CONSOLIDADA"
            lista.save()
            lista.listas_unidas.update(status="CONSOLIDADA")
            messages.success(request, "Lista consolidada com sucesso!")
            return redirect('lista_compras')
        
        # Botão Processar Compra
        if "EM_PROCESSO_COMPRA" in request.POST:
            if request.user.tipo_usuario != "GESTOR_MATRIZ":
                messages.error(request, "Você não tem permissão para processar compras.")
                return redirect("lista_compras")
            lista.status = "EM_PROCESSO_COMPRA"
            lista.save()
            lista.listas_unidas.update(status="EM_PROCESSO_COMPRA")
            messages.success(request, "Lista atualizada para processo de compra e propagada para unidas!")
            return redirect("lista_compras")
        
        # Botão Finalizar Compra
        if "RECEBIDA" in request.POST:
            if request.user.tipo_usuario != "GESTOR_MATRIZ" and request.user.tipo_usuario != "GESTOR_FILIAL" and lista.status != "EM_ENTREGA":
                messages.error(request, "Você não tem permissão para finalizar compras.")
                return redirect("lista_compras")

            # percorre todos os itens da lista e adiciona ao estoque da empresa
            for item in itens:
                estoque, created = Estoque.objects.get_or_create(
                    empresa=lista.empresa,
                    produto=item.produto,
                    defaults={'quantidade': 0, 'quantidade_minima': 0}
                )
                estoque.quantidade += item.quantidade_desejada
                estoque.save()

                 # registra log de entrada
                LogEntrada.objects.create(
                    usuario=request.user,
                    empresa=lista.empresa,
                    produto=item.produto,
                    quantidade=item.quantidade_desejada
                )

            lista.status = "RECEBIDA"
            lista.save()

             # atualiza status apenas das listas unidas da mesma empresa
            lista.listas_unidas.filter(empresa=lista.empresa).update(status="RECEBIDA")

            messages.success(request, "Itens recebidos e adicionados ao estoque com sucesso!")
            return redirect("lista_compras")

        # Botão Em Rota de Entrega
        if "EM_ENTREGA" in request.POST:
            if request.user.tipo_usuario != "GESTOR_MATRIZ":
                messages.error(request, "Você não tem permissão para atualizar o status de entrega.")
                return redirect("lista_compras")
            lista.status = "EM_ENTREGA"
            lista.save()
            messages.success(request, "Status atualizado para Em Rota de Entrega!")
            return redirect("lista_compras")

        # Botão Atualizar Status de listas unidas
        if "atualizar_status" in request.POST:
            novo_status = request.POST.get("status")
            if novo_status:
                lista.status = novo_status
                lista.save()
                # Propagar para unidas (listas ligadas a esta como principal)
                lista.listas_unidas.update(status=novo_status)
                messages.success(request, f"Status atualizado para {novo_status} e propagado.")
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


@login_required(login_url='/login/')
def unir_listas(request):
    if request.method != "POST":
        messages.error(request, "Operação inválida.")
        return redirect("lista_compras")

    ids = request.POST.getlist("listas_selecionadas")
    if not ids:
        messages.warning(request, "Selecione ao menos uma lista autorizada.")
        return redirect("lista_compras")

    # pega todas as listas autorizadas, independente da empresa
    listas_sel = ListaCompra.objects.filter(id__in=ids, status="AUTORIZADA")
    if not listas_sel.exists():
        messages.error(request, "Nenhuma lista autorizada selecionada.")
        return redirect("lista_compras")

    with transaction.atomic():
        # gerar número sequencial para a empresa do usuário logado
        empresa_usuario = request.user.empresa
        ultimo = ListaCompra.objects.filter(empresa=empresa_usuario).order_by('id').last()
        numero_seq = int(ultimo.numero.split('/')[0]) + 1 if ultimo else 1
        numero = f"{str(numero_seq).zfill(5)}/{timezone.now().year}"

        # nova lista sempre da empresa do usuário logado
        nova_lista = ListaCompra.objects.create(
            numero=numero,
            empresa=empresa_usuario,
            criado_por=request.user,
            status="Em processo de consolidação"
        )

        # associa as listas selecionadas
        nova_lista.listas_unidas.set(listas_sel)

        # agrega itens de TODAS as listas selecionadas
        itens_agregados = (
            ItemListaCompra.objects
            .filter(lista__in=listas_sel)
            .values('produto')
            .annotate(total_qtd=Sum('quantidade_desejada'))
        )

        for item in itens_agregados:
            produto = Produto.objects.get(id=item['produto'])
            ItemListaCompra.objects.create(
                lista=nova_lista,
                produto=produto,
                quantidade_desejada=item['total_qtd']
            )

        # atualiza status de todas as selecionadas
        listas_sel.update(status="UNIDA")

    messages.success(request, f"Lista {nova_lista.numero} criada para {empresa_usuario.nome} e listas unidas com sucesso.")
    return redirect("lista_compras")

