# 📦 Projeto HIDROMANAGER
Este projeto é um sistema web desenvolvido com Django, para gerenciar o estoque de produtos em uma empresa. Ele permite o controle de fornecedores, produtos, entradas e saídas de estoque, além de facilitar a gestão de compras e usuários com diferentes néveis de acesso(gerente e funcionário).

## Desenvolvido com
* Python
* Django

## Estrutura do projeto
### Apps
* usuarios - Gerencia autenticação, cadastro, permisões e perfis de usuários(gerente e funcionário).
* fornecedores - Armazena dados de fornecedores de produtos.
* produtos - Controla o catálogo de produtos.
* estoque - Monitora a quantidade de produtos em estoque e alerta sobre níveis mínimos.
* compras - Registra lista de compras e itens solicitados para reposição do estoque.
* retiradas - Gerencia retiradas de produtos por funcionários e atualiza o estoque.

### Fluxo de funcionamento
1. Usuários fazem login no sistema (gerente ou funcionário).
2. Funcionários podem registar retiradas de produtos.
3. O sistema atualiza automaticamente o estoque.
4. Quando o estoque atinge nível mínimo, o gerente pode gerar uma lista de compras.
5. Os produtos são adquiridos de fornecedores previamente cadastrados.
6. As compras são registradas e os produtos são adicionados ao estoque.

### Requisitos para rodar e editar o projeto
* Visual Studio Code;
* Uma conta no git-hub e git instalado;
* 

### Como rodar o projeto no windows
#### No terminal do vs code digite:
1. `git clone https://github.com/projetoempy/HIDROGEST.git` (baixa os arquivos do projeto)
2. `cd HIDROGEST` (entra na pasta)
3. `python -m venv .venv` (cria um ambiente virtual)
4. `.venv/Scripts/activate` (ativa o ambiente virtual)
5. `pip install django` (instala o Django no ambiente virtual)
6. `python manage.py makemigrations` (detecta alterações nos modelos em `models.py` e cria arquivos dentro da pasta `migrations/` de cada app, esses arquivos descrevem as mudanças, mas não altera nada no banco de dados, penas prepara os arquivos)
7. `python manage.py migrate` (executa as migrações criadas, ou seja, aplica as mudanças no banco de dados)
8. `python manage.py createsuperuser` (cria um usuário administrador no banco de dados)
9. `python manage.py populate` (insere dados fictícios do arquivo `usuarios/management/commands/populate.py` no banco de dados)
10. `python manage.py runserver` (roda o servdor. (Abra o navegador de internet e digite: `http://127.0.0.1:8000/`, para abrir o site do projeto))
