from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.

from django.contrib.auth.decorators import login_required
from produtos.models import Produto
from estoque.models import Estoque
from .forms import RetiradaForm

@login_required
def dashboard_funcionario(request):
    if request.user.tipo != 'funcionario':
        return redirect('home')

    #produtos = Produto.objects.all()
    estoques = Estoque.objects.select_related('produto').all()
    return render(request, 'retiradas/dashboard_funcionario.html', {'estoques': estoques})

@login_required
def retirar_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    estoque = get_object_or_404(Estoque, produto=produto)

    if request.method == 'POST':
        form = RetiradaForm(request.POST)
        if form.is_valid():
            retirada = form.save(commit=False)
            retirada.produto = produto
            retirada.funcionario = request.user

            if retirada.quantidade > 0 and retirada.quantidade <= estoque.quantidade:
                # Atualiza o estoque
                estoque.quantidade -= retirada.quantidade
                estoque.save()

                # Salva a retirada
                retirada.save()

                # Redireciona para o dashboard
                return redirect('dashboard_funcionario')
            else:
                form.add_error('quantidade', 'Quantidade inválida ou insuficiente em estoque.')
    else:
        form = RetiradaForm()

    return render(request, 'retiradas/retirar_produto.html', {
        'form': form, 
        'produto': produto,
        'estoque': estoque})