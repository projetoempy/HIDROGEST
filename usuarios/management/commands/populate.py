from django.core.management.base import BaseCommand
from fornecedores.models import Fornecedor
from produtos.models import Produto
from estoque.models import Estoque

class Command(BaseCommand):
    help = 'Popula o banco com 1 fornecedor, 5 produtos e entradas no estoque'

    def handle(self, *args, **kwargs):
        fornecedor = Fornecedor.objects.create(
            nome_empresa='HidroTech',
            cnpj='00.111.222/0001-33',
            endereco='Av. das Águas, 456',
            site='https://hidrotech.com.br',
            telefone='(91) 98888-1234',
            email='contato@hidrotech.com.br'
        )

        produtos = [
            {'nome': 'Bomba Submersa', 'preco': 320.00, 'descricao': 'Ideal para poços e cisternas'},
            {'nome': 'Torneira Inteligente', 'preco': 85.50, 'descricao': 'Economiza água com sensor de presença'},
            {'nome': 'Mangueira Flexível 10m', 'preco': 45.90, 'descricao': 'Alta resistência e flexibilidade'},
            {'nome': 'Purificador Compacto', 'preco': 210.00, 'descricao': 'Filtro de carvão ativado com UV'},
            {'nome': 'Kit Irrigação Automática', 'preco': 399.99, 'descricao': 'Sistema completo para jardins'}
        ]

        for item in produtos:
            produto = Produto.objects.create(
                nome=item['nome'],
                preco=item['preco'],
                descricao=item['descricao'],
                fornecedor=fornecedor
            )
            Estoque.objects.create(
                produto=produto,
                quantidade=20,
                quantidade_minima=5
            )

        self.stdout.write(self.style.SUCCESS('5 produtos cadastrados com sucesso!'))