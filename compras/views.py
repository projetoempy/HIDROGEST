from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum

from .models import ListaCompra, ItemListaCompra, LogAlteracaoLista
from produtos.models import Produto
from fornecedores.models import Fornecedor
from estoques.models import Estoque, LogEntrada, LogRetirada


# -------------------------------
# Funções utilitárias
# -------------------------------

def registrar_log(lista, produto, usuario, antiga, nova):
    """Registra alterações de quantidade em uma lista de compras."""
    LogAlteracaoLista.objects.create(
        lista=lista,
        produto=produto,
        alterado_por=usuario,
        quantidade_antiga=antiga,
        quantidade_nova=nova,
        data_hora=timezone.now()
    )


def congelar_precos(lista):
    """Congela preços dos itens de uma lista."""
    for item in lista.itens.all():
        if not item.preco_unitario:
            item.preco_unitario = item.produto.preco
            item.save()


# -------------------------------
# Views principais
# -------------------------------

@login_required(login_url='/login/')
def lista_compras(request):
    """Lista todas as compras visíveis para o usuário."""
    if request.user.tipo_usuario in ["GERENTE_MATRIZ", "GESTOR_MATRIZ"]:
        listas = ListaCompra.objects.exclude(
            status__in=["EM_CRIACAO", "EM_PROCESSO_AUTORIZACAO"]
        ) | ListaCompra.objects.filter(
            empresa=request.user.empresa,
            status__in=["EM_CRIACAO", "EM_PROCESSO_AUTORIZACAO"]
        )
    else:
        listas = ListaCompra.objects.filter(empresa=request.user.empresa)

    # Filtros
    empresa_nome = request.GET.get('empresa') or ""
    status = request.GET.get('status')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    principal = request.GET.get('principal')

    if empresa_nome:
        listas = listas.filter(empresa__nome__icontains=empresa_nome)
    if status:
        listas = listas.filter(status=status)
    if data_inicio:
        listas = listas.filter(data_criacao__date__gte=data_inicio)
    if data_fim:
        listas = listas.filter(data_criacao__date__lte=data_fim)

    # Principais e unidas
    principais = listas.filter(listas_unidas__isnull=False).distinct()
    unidas = listas.filter(status="UNIDA")


    # aplica filtro de principal/unidas
    if principal == "principais":
        listas = principais  # mostra só as listas principais (que têm unidas)
    elif principal == "unidas":
        listas = unidas # só as listas unidas (que pertencem a uma principal)

     # Correção
    # Se 'listas' for um QuerySet, use .filter; se for lista Python, use 'any'
    tem_autorizada = listas.filter(status="AUTORIZADA").exists()
    tem_unida = listas.filter(status="UNIDA").exists()
    tem_consolidada = listas.filter(status="CONSOLIDADA").exists()


    contexto = {
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
        'header_title': "Listas de Compra",
    }
    return render(request, 'compras/listas.html', contexto)


@login_required(login_url='/login/')
def criar_lista(request):
    """Cria uma nova lista de compras."""
    empresa = request.user.empresa
    ano_atual = timezone.now().year

    if request.method == "POST":
        # pega apenas listas do ano atual

        ultimo = ListaCompra.objects.filter(
            empresa=empresa, 
            numero__endswith=f"/{ano_atual}"
        ).order_by('id').last()
        # se não houver nenhuma lista no ano atual, começa em 1

        numero_seq = int(ultimo.numero.split('/')[0]) + 1 if ultimo else 1
        # monta o número com 5 dígitos e ano atual
        numero = f"{str(numero_seq).zfill(5)}/{ano_atual}"

        lista = ListaCompra.objects.create(
            numero=numero,
            empresa=empresa,
            criado_por=request.user,
            status='EM_CRIACAO'
        )

        # Adiciona produtos
        for produto in Produto.objects.all():
            qtd = int(request.POST.get(f"produto_{produto.id}", 0))
            if qtd > 0:
                ItemListaCompra.objects.create(
                    lista=lista,
                    produto=produto,
                    quantidade_desejada=qtd,
                    preco_unitario=produto.preco
                )

        messages.success(request, f"Lista {lista.numero} criada com sucesso!")
        return redirect('detalhes_lista', id=lista.id)

    fornecedores = Fornecedor.objects.all().prefetch_related('produtos')
    return render(request, 'compras/cadastro_lista.html', {
        'empresa': empresa,
        'fornecedores': fornecedores,
        'header_title': "Nova Lista de Compras",
    })


@login_required(login_url='/login/')
def detalhes_lista(request, id):
    """Detalhes de uma lista de compras, com ações de status e edição de itens."""
    lista = get_object_or_404(ListaCompra, id=id)
    itens = ItemListaCompra.objects.filter(lista=lista)
    alteracoes = LogAlteracaoLista.objects.filter(lista=lista)
    fornecedores = Fornecedor.objects.all().prefetch_related('produtos')
    
    # Filtro de produto por nome
    filtro_nome = request.GET.get("produto_nome", "")
    fornecedores = Fornecedor.objects.all().prefetch_related('produtos')

    if filtro_nome:
        for fornecedor in fornecedores:
            fornecedor.produtos_filtrados = fornecedor.produtos.filter(nome__icontains=filtro_nome)
    else:
        for fornecedor in fornecedores:
            fornecedor.produtos_filtrados = fornecedor.produtos.all()


    # Calcular preço total de cada item e valor total da lista
    itens_com_preco = []
    for item in itens:
        preco_unitario = item.preco_unitario or item.produto.preco
        preco_total = item.quantidade_desejada * preco_unitario
        itens_com_preco.append({
            'obj': item,
            'preco_unitario': preco_unitario,
            'preco_total': preco_total
        })
    total_lista = sum(i['preco_total'] for i in itens_com_preco)

    # -------------------------------
    # Ações via POST
    # -------------------------------
    if request.method == "POST":

        # Solicitar autorização
        if "solicitar_autorizacao" in request.POST:
            if request.user.tipo_usuario not in ["GESTOR_MATRIZ", "GESTOR_FILIAL"]:
                messages.error(request, "Você não tem permissão para processar compras.")
                return redirect("lista_compras")
            lista.status = "EM_PROCESSO_AUTORIZACAO"
            lista.save()
            messages.success(request, "Solicitação de autorização enviada!")
            return redirect("lista_compras")

        # Autorizar lista
        elif "AUTORIZADA" in request.POST:
            if request.user.tipo_usuario not in ["GERENTE_MATRIZ", "GERENTE_FILIAL"]:
                messages.error(request, "Você não tem permissão para autorizar compras.")
                return redirect("lista_compras")
            lista.status = "AUTORIZADA"
            lista.save()
            messages.success(request, "Lista autorizada com sucesso!")
            return redirect("lista_compras")

        # Consolidar lista
        elif "CONSOLIDADA" in request.POST:
            if request.user.tipo_usuario != "GERENTE_MATRIZ":
                messages.error(request, "Você não tem permissão para consolidar compras.")
                return redirect("lista_compras")
            lista.status = "CONSOLIDADA"
            lista.save()
            lista.listas_unidas.update(status="CONSOLIDADA")
            messages.success(request, "Lista consolidada com sucesso!")
            return redirect("lista_compras")

        # Processar compra
        elif "EM_PROCESSO_COMPRA" in request.POST:
            if request.user.tipo_usuario != "GESTOR_MATRIZ":
                messages.error(request, "Você não tem permissão para processar compras.")
                return redirect("lista_compras")
            lista.status = "EM_PROCESSO_COMPRA"
            lista.save()
            lista.listas_unidas.update(status="EM_PROCESSO_COMPRA")
            messages.success(request, "Lista atualizada para processo de compra e propagada para unidas!")
            return redirect("lista_compras")

        # Receber itens
        elif "RECEBIDA" in request.POST:
            if request.user.tipo_usuario not in ["GESTOR_MATRIZ", "GESTOR_FILIAL"] and lista.status != "EM_ENTREGA":
                messages.error(request, "Você não tem permissão para finalizar compras.")
                return redirect("lista_compras")

            # Congela preços da lista principal
            congelar_precos(lista)
            
            # Atualiza estoque da lista principal
            for item in itens:
                estoque, _ = Estoque.objects.get_or_create(
                    empresa=lista.empresa,
                    produto__nome=item.produto.nome,
                    defaults={'produto': item.produto,'quantidade': 0, 'quantidade_minima': 0}
                )
                estoque.quantidade += item.quantidade_desejada
                estoque.save()
                LogEntrada.objects.create(
                    usuario=request.user,
                    empresa=lista.empresa,
                    produto=item.produto,
                    quantidade=item.quantidade_desejada
                )

            # Congela preços e atualiza status das listas unidas
            for lista_unida in lista.listas_unidas.filter(empresa=lista.empresa).all():
                # Congela preços da lista unida
                congelar_precos(lista_unida)
                 # Atualiza estoque das listas unidas
                lista_unida.status = "RECEBIDA"
                lista_unida.save()

            lista.status = "RECEBIDA"
            lista.save()
            messages.success(request, "Itens recebidos e adicionados ao estoque com sucesso!")
            return redirect("lista_compras")

        # Enviar itens (rota de entrega)
        elif "EM_ENTREGA" in request.POST:
            if request.user.tipo_usuario != "GESTOR_MATRIZ":
                messages.error(request, "Você não tem permissão para atualizar o status de entrega.")
                return redirect("lista_compras")

            for item in itens:
                estoque_matriz, _ = Estoque.objects.get_or_create(
                    empresa=request.user.empresa,
                    produto=item.produto,
                    defaults={'quantidade': 0, 'quantidade_minima': 0}
                )

                # Verifica se há estoque suficiente
                if estoque_matriz.quantidade < item.quantidade_desejada:
                    messages.error(request, f"Estoque insuficiente para {item.produto.nome}.")
                    return redirect("detalhes_lista", id=lista.id)

                # Deduz quantidade enviada
                estoque_matriz.quantidade -= item.quantidade_desejada
                estoque_matriz.save()

                # Registra como retirada
                LogRetirada.objects.create(
                    usuario=request.user,
                    empresa=request.user.empresa,
                    destino = lista.empresa,
                    produto=item.produto,
                    quantidade=item.quantidade_desejada
                )

            lista.status = "EM_ENTREGA"
            lista.save()
            messages.success(request, "Status atualizado para Em Rota de Entrega!")
            return redirect("lista_compras")

        # Atualizar status manualmente
        elif "atualizar_status" in request.POST:
            novo_status = request.POST.get("status")
            if novo_status:
                lista.status = novo_status
                lista.save()
                lista.listas_unidas.update(status=novo_status)
                messages.success(request, f"Status atualizado para {novo_status} e propagado.")
                return redirect('detalhes_lista', id=lista.id)

        # Adicionar novos produtos + Alterações nos itens
        else:
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

            messages.success(request, "Alterações salvas com sucesso!")
            return redirect('detalhes_lista', id=lista.id)

    # Renderização padrão
    return render(request, 'compras/detalhes.html', {
        'lista': lista,
        'itens': itens_com_preco,
        'alteracoes': alteracoes,
        'fornecedores': fornecedores,
        'total_lista': total_lista,
        'header_title': f"Detalhes da Lista {lista.numero}",
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
        messages.error(request, "Selecione ao menos uma lista autorizada para clicar em Unir Listas.")
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
            status="EM_PROCESSO_CONSOLIDACAO"
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



@login_required(login_url='/login/')
def enviar_lista(request):
    if request.method != "POST":
        messages.error(request, "Operação inválida.")
        return redirect("lista_compras")

    lista_id = request.POST.get("lista_id")

    # Nenhuma lista selecionada
    if not lista_id or lista_id.strip() == "":
        messages.error(request, "Nenhuma lista selecionada para enviar.")
        return redirect("lista_compras")

    # Mais de uma lista selecionada
    if lista_id == "MULTIPLAS":
        messages.error(request, "Erro: selecione apenas uma lista para enviar itens.")
        return redirect("lista_compras")

    # Busca a lista autorizada
    lista = get_object_or_404(ListaCompra, id=lista_id, status="AUTORIZADA")

    # Verifica estoque
    itens = ItemListaCompra.objects.filter(lista=lista)
    for item in itens:
        estoque, _ = Estoque.objects.get_or_create(
            empresa=request.user.empresa,
            produto=item.produto,
            defaults={'quantidade': 0, 'quantidade_minima': 0}
        )
        if estoque.quantidade < item.quantidade_desejada:
            messages.error(request, f"Estoque insuficiente para {item.produto.nome}.")
            return redirect("lista_compras")

    # Deduz e registra retirada
    for item in itens:
        estoque = Estoque.objects.get(empresa=request.user.empresa, produto=item.produto)
        estoque.quantidade -= item.quantidade_desejada
        estoque.save()
        LogRetirada.objects.create(
            usuario=request.user,
            empresa=request.user.empresa,
            destino = lista.empresa,
            produto=item.produto,
            quantidade=item.quantidade_desejada
        )

    # Atualiza status da lista
    lista.status = "EM_ENTREGA"
    lista.save()

    messages.success(request, f"Lista {lista.numero} enviada para entrega.")
    return redirect("lista_compras")