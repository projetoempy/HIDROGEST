from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.

from .models import Estoque, LogRetirada, LogEntrada
from django.contrib.auth.decorators import login_required

from django.contrib import messages

from empresas.models import Empresa
from produtos.models import Produto

from django.db import models

from django.utils.dateparse import parse_date
from datetime import date, timedelta

@login_required(login_url='/login/')
def lista_estoques(request):
    usuario = request.user
    empresa_usuario = usuario.empresa
    

    # Se for gerente ou gestor da matriz → vê todos os estoques
    if usuario.tipo_usuario in ["GERENTE_MATRIZ", "GESTOR_MATRIZ"]:
        estoques = Estoque.objects.all()
    else:
        # Funcionários de filial → só veem estoques da própria empresa
        estoques = Estoque.objects.filter(empresa=empresa_usuario)
    # Filtro por nome do produto
    produto_nome = request.GET.get('produto') or ''
    if produto_nome:
        estoques = estoques.filter(produto__nome__icontains=produto_nome)

    return render(request, 'estoques/estoques.html', {
        'estoques': estoques,
        'empresa_usuario': empresa_usuario,
        'produto_nome': produto_nome,
        'header_title': 'Estoques',
    })

@login_required(login_url='/login/')
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
        if Estoque.objects.filter(empresa=empresa, produto=produto).exists():
            messages.error(request, f"Não pôde ser cadastrado o produto {produto.nome}, pois o estoque da empresa {empresa.nome} contêm o mesmo. Basta editá-lo!")
            return render(request, 'estoques/cadastro_estoque.html', {
                'empresas': empresas,
                'produtos': produtos,
                'empresa': empresa,
                'header_title': 'Adicionar Produto ao Estoque'
            })

        Estoque.objects.create(empresa=empresa, produto=produto, quantidade=quantidade, quantidade_minima=quantidade_minima)
        messages.success(request, "Produto adicionado ao estoque com sucesso!")
        return redirect('lista_estoques')
    return render(request, 'estoques/cadastro_estoque.html', {
        'empresas': empresas, 
        'produtos': produtos, 
        'empresa': empresa
    })

@login_required(login_url='/login/')
def editar_estoque(request, id):
    estoque = get_object_or_404(Estoque, id=id)
    empresas = Empresa.objects.all()
    produtos = Produto.objects.all()
    if request.method == "POST":
        empresa_id = request.POST.get('empresa')
        if empresa_id:
            estoque.empresa = Empresa.objects.get(id=empresa_id)
        else:
            estoque.empresa = request.user.empresa  # fallback
        estoque.produto = Produto.objects.get(id=request.POST['produto'])
        estoque.quantidade = request.POST['quantidade']
        estoque.quantidade_minima = request.POST['quantidade_minima']
        estoque.save()
        messages.success(request, "Estoque atualizado com sucesso!")
        return redirect('lista_estoques')
    return render(request, 'estoques/cadastro_estoque.html', {
        'estoque': estoque, 
        'empresas': empresas, 
        'produtos': produtos,
        'header_title': 'Editar Estoque',
    })

@login_required(login_url='/login/')
def excluir_estoque(request, id):
    estoque = get_object_or_404(Estoque, id=id)
    estoque.delete()
    messages.success(request, "Estoque excluído com sucesso!")
    return redirect('lista_estoques')


# Função auxiliar para contar entradas/saídas por período
def contar_por_periodo(modelo, empresa, inicio, fim):
    return modelo.objects.filter(empresa=empresa, data_hora__date__gte=inicio, data_hora__date__lte=fim).count()


@login_required(login_url='/login/')
def ver_logs(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)

    # Filtros
    tipo = request.GET.get('tipo')  # entradas ou saídas
    funcionario = request.GET.get('funcionario') or ''
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    # Datas de referência
    hoje = date.today()
    inicio_ano = hoje.replace(month=1, day=1)
    inicio_mes = hoje.replace(day=1)
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    inicio_trimestre = hoje.replace(month=((hoje.month - 1) // 3) * 3 + 1, day=1)
    # Períodos anteriores
    ano_anterior = inicio_ano.replace(year=inicio_ano.year - 1)
    mes_anterior = (inicio_mes - timedelta(days=1)).replace(day=1)
    semana_anterior = inicio_semana - timedelta(days=7)
    trimestre_anterior = (inicio_trimestre - timedelta(days=1)).replace(day=1)

    # Contagens
    def contar(modelo, empresa, ini, fim):
        return modelo.objects.filter(
            empresa=empresa, 
            data_hora__date__gte=ini, 
            data_hora__date__lte=fim
            ).aggregate(total=models.Sum("quantidade"))["total"] or 0

    cards = {
        "ano": {
            "entrada": {
                "anterior": contar(LogEntrada, empresa, ano_anterior, inicio_ano - timedelta(days=1)),
                "atual": contar(LogEntrada, empresa, inicio_ano, hoje),
            },
            "saida": {
                "anterior": contar(LogRetirada, empresa, ano_anterior, inicio_ano - timedelta(days=1)),
                "atual": contar(LogRetirada, empresa, inicio_ano, hoje),
            },
            "saldo": {
                "anterior": contar(LogEntrada, empresa, ano_anterior, inicio_ano - timedelta(days=1))
                            - contar(LogRetirada, empresa, ano_anterior, inicio_ano - timedelta(days=1)),
                "atual": contar(LogEntrada, empresa, inicio_ano, hoje)
                            - contar(LogRetirada, empresa, inicio_ano, hoje),
            },
        },
        "trimestre": {
            "entrada": {
                "anterior": contar(LogEntrada, empresa, trimestre_anterior, inicio_trimestre - timedelta(days=1)),
                "atual": contar(LogEntrada, empresa, inicio_trimestre, hoje),
            },
            "saida": {
                "anterior": contar(LogRetirada, empresa, trimestre_anterior, inicio_trimestre - timedelta(days=1)),
                "atual": contar(LogRetirada, empresa, inicio_trimestre, hoje),
            },
            "saldo": {
                "anterior": contar(LogEntrada, empresa, trimestre_anterior, inicio_trimestre - timedelta(days=1))
                            - contar(LogRetirada, empresa, trimestre_anterior, inicio_trimestre - timedelta(days=1)),
                "atual": contar(LogEntrada, empresa, inicio_trimestre, hoje)
                            - contar(LogRetirada, empresa, inicio_trimestre, hoje),
            },
        },
        "mes": {
            "entrada": {
                "anterior": contar(LogEntrada, empresa, mes_anterior, inicio_mes - timedelta(days=1)),
                "atual": contar(LogEntrada, empresa, inicio_mes, hoje),
            },
            "saida": {
                "anterior": contar(LogRetirada, empresa, mes_anterior, inicio_mes - timedelta(days=1)),
                "atual": contar(LogRetirada, empresa, inicio_mes, hoje),
            },
            "saldo": {
                "anterior": contar(LogEntrada, empresa, mes_anterior, inicio_mes - timedelta(days=1))
                            - contar(LogRetirada, empresa, mes_anterior, inicio_mes - timedelta(days=1)),
                "atual": contar(LogEntrada, empresa, inicio_mes, hoje)
                            - contar(LogRetirada, empresa, inicio_mes, hoje),
            },
        },
        "semana": {
            "entrada": {
                "anterior": contar(LogEntrada, empresa, semana_anterior, inicio_semana - timedelta(days=1)),
                "atual": contar(LogEntrada, empresa, inicio_semana, hoje),
            },
            "saida": {
                "anterior": contar(LogRetirada, empresa, semana_anterior, inicio_semana - timedelta(days=1)),
                "atual": contar(LogRetirada, empresa, inicio_semana, hoje),
            },
            "saldo": {
                "anterior": contar(LogEntrada, empresa, semana_anterior, inicio_semana - timedelta(days=1))
                            - contar(LogRetirada, empresa, semana_anterior, inicio_semana - timedelta(days=1)),
                "atual": contar(LogEntrada, empresa, inicio_semana, hoje)
                            - contar(LogRetirada, empresa, inicio_semana, hoje),
            },
        },
    }



    logs_entrada = LogEntrada.objects.filter(empresa=empresa)
    logs_saida = LogRetirada.objects.filter(empresa=empresa)

    # Adiciona atributo 'tipo' para cada log
    for log in logs_entrada:
        log.tipo = "Entrada"
    for log in logs_saida:
        log.tipo = "Saída"

    # Filtrar por tipo
    if tipo == "entrada":
        logs = logs_entrada
    elif tipo == "saida":
        logs = logs_saida
    else:
        # junta entradas e saídas
        logs = list(logs_entrada) + list(logs_saida)

    # Filtrar por funcionário
    if funcionario:
        logs = [log for log in logs if log.usuario.username == funcionario]

    # Filtrar por período
    if data_inicio:
        di = parse_date(data_inicio)
        logs = [log for log in logs if log.data_hora.date() >= di]
    if data_fim:
        df = parse_date(data_fim)
        logs = [log for log in logs if log.data_hora.date() <= df]

    return render(request, "estoques/logs.html", {
        "empresa": empresa,
        "logs": logs,
        "cards": cards,
        "tipo": tipo,
        "funcionario": funcionario,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "header_title": "Ver Logs",
    })



@login_required(login_url='/login/')
def retirar_estoque(request, id):
    estoque = get_object_or_404(Estoque, id=id, empresa=request.user.empresa)

    if request.method == "POST":
        qtd = int(request.POST.get('quantidade', 0))
        if qtd > 0 and qtd <= estoque.quantidade:
            estoque.quantidade -= qtd
            estoque.save()

            # registra log de retirada
            LogRetirada.objects.create(
                usuario=request.user,
                empresa=request.user.empresa,
                produto=estoque.produto,
                quantidade=qtd
            )

            messages.success(request, f"{qtd} unidades de {estoque.produto.nome} retiradas do estoque.")
        else:
            messages.error(request, "Quantidade inválida para retirada.")

    return redirect('dashboard')