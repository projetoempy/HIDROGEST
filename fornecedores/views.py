from django.shortcuts import render
from usuarios.views import login_required

# Create your views here.
from django.shortcuts import render, redirect
from .forms import FornecedorForm
from .models import Fornecedor

@login_required
def cadastrar_fornecedor(request):
    if request.method == 'POST':
        form = FornecedorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard_gerente')
    else:
        form = FornecedorForm()
    return render(request, 'fornecedores/cadastro_fornecedor.html', {'form': form})


def lista_fornecedores(request):
    fornecedores = Fornecedor.objects.all()
    return render(request, 'fornecedores/lista_fornecedores.html', {'fornecedores': fornecedores})