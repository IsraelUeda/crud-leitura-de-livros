# CRUD de Leitura de Livros

Este projeto é uma aplicação web simples em Flask para gerenciar uma coleção de livros.
Ela permite adicionar, editar, visualizar, deletar e pesquisar livros, além de importar dados da Open Library e fazer upload de arquivos PDF.

## Funcionalidades

- Lista de livros cadastrados
- Tela de cadastro de novos livros
- Edição de dados de livros
- Exclusão de livros
- Visualização de detalhes de livros
- Upload e exibição de PDF associados ao livro
- Busca de livros usando a API da Open Library
- Importação de resultados de busca para a biblioteca local
- Mostrador de estante com interface dinâmica (rota `/estante`)

## Tecnologias

- Python 3
- Flask
- PostgreSQL
- HTML/CSS/JavaScript

## Estrutura do projeto

- `app.py` - aplicação principal Flask
- `templates/` - páginas HTML
- `static/` - arquivos estáticos (CSS, JS)
- `uploads/` - PDFs enviados via formulário

## Requisitos

- Python 3.8 ou superior
- Flask

## Instalação e execução

1. Crie e ative um ambiente virtual (opcional, mas recomendado):

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Configure a variável de ambiente `DATABASE_URL` com a URL do PostgreSQL, por exemplo:

```bash
export DATABASE_URL='postgresql://user:password@host:port/dbname'
```

4. Execute a aplicação:

```bash
python app.py
```

5. Acesse no navegador:

```
http://127.0.0.1:5000/
```

> A pasta `uploads/` é criada automaticamente na primeira execução. O banco é gerenciado no PostgreSQL definido em `DATABASE_URL`.

## Como usar

- Vá para `/` para ver a lista de livros.
- Use `/adicionar` para cadastrar um novo livro.
- Use `/buscar` para pesquisar títulos na Open Library e importar resultados.
- Use `/estante` para ver a estante interativa.
- Nos detalhes do livro, é possível enviar um PDF e visualizar o arquivo.

## Notas adicionais

- Apenas arquivos `.pdf` são aceitos para upload.
- Se o livro for excluído, o PDF correspondente também é removido do servidor.
- O campo `cor` do livro é usado para personalizar a exibição na estante.
