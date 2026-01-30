# 📦 Projeto HIDROMANAGER
Este projeto é um sistema web desenvolvido com **Django**, voltado para o gerenciamento de pedidos e controle de estoque da matriz e das filiais de uma empresa.  
A aplicação oferece funcionalidades completas para:  

- **Administração de pedidos e compras** 
- **Gestão de fornecedores e produtos**  
- **Controle de entradas e saídas de estoque**  
- **Gerenciamento de usuários com diferentes níveis de acesso**, incluindo:  
  - Gerente da matriz  
  - Gerente da filial  
  - Gestor da matriz  
  - Gestor da filial  
  - Funcionário  

Com isso, o sistema centraliza e simplifica os processos de compras e estoque, garantindo maior organização, segurança e eficiência na operação da empresa.

## Desenvolvido com
* Python
* Django

## Estrutura do projeto
### Apps
* usuarios - Gerencia autenticação, cadastro, permisões e perfis de usuários(gerentes, gestores e funcionários).
* fornecedores - Armazena dados de fornecedores de produtos.
* produtos - Controla o catálogo de produtos de cada fornecedor.
* estoque - Monitora a retirada e a quantidade de produtos em estoque e alerta sobre níveis mínimos.
* compras - Registra lista de compras e itens solicitados para reposição do estoque da matriz e das filiais.
* empresas - Gerencia a matriz e as filiais.

### Fluxo de funcionamento
1. Usuários fazem login no sistema (gerente, gestor ou funcionário).
2. Funcionários podem registar retiradas de produtos.
3. O sistema atualiza automaticamente o estoque.
4. Quando o estoque atinge nível mínimo, o gestor pode gerar uma lista de compras que terá status 'Em análise' → 'Autorizada' → '.
5. Os produtos são adquiridos de fornecedores previamente cadastrados.
6. As compras são registradas e os produtos são adicionados ao estoque.

### Requisitos para rodar e editar o projeto
* Visual Studio Code;
* Uma conta no git-hub e git instalado;
* 

### Como rodar o projeto no windows
#### No terminal do vs code digite:
1. `git clone -b Jailson https://github.com/projetoempy/HIDROGEST.git` (baixa os arquivos do projeto)
2. `cd HIDROGEST` (entra na pasta)
3. `python -m venv .venv` (cria um ambiente virtual)
4. `.venv/Scripts/activate` (ativa o ambiente virtual)
5. `pip install django` (instala o Django no ambiente virtual)
6. `python manage.py runserver` (roda o servdor. (Abra o navegador de internet e digite: `http://127.0.0.1:8000/`, para abrir o site do projeto))
7. para acessar o banco de dados do django digite no navegador de internet: `http://127.0.0.1:8000/admin` (usuário: admin; senha: 0123456789)
