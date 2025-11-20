from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.

from .models import Estoque

def atualizar_minimo(request, estoque_id):
    if request.method == 'POST':
        novo_valor = request.POST.get('quantidade_minima')
        estoque = get_object_or_404(Estoque, id=estoque_id)
        if novo_valor.isdigit():
            estoque.quantidade_minima = int(novo_valor)
            estoque.save()
    return redirect('dashboard_gerente')