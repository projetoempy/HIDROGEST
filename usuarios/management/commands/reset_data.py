from django.core.management.base import BaseCommand
from fornecedores.models import Fornecedor
from produtos.models import Produto
from estoque.models import Estoque
from compras.models import ListaCompra, ItemCompra
from retiradas.models import Retirada

class Command(BaseCommand):
    help = 'Apaga todos os dados de fornecedores, produtos, estoque, compras e retiradas'

    def handle(self, *args, **kwargs):
        Retirada.objects.all().delete()
        ItemCompra.objects.all().delete()
        ListaCompra.objects.all().delete()
        Estoque.objects.all().delete()
        Produto.objects.all().delete()
        Fornecedor.objects.all().delete()

        self.stdout.write(self.style.WARNING('Todos os dados foram apagados com sucesso.'))