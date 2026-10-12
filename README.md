# Doce Encanto — Projeto Integrador II

Continuação do **Sistema Mobile para Loja Virtual de Cupcakes Gourmet**, da disciplina Projeto Integrador Transdisciplinar em Engenharia de Software I. Protótipo funcional em **web responsiva** com Flask, SQLite e templates HTML/CSS.

## Executar localmente

Requisitos: Python 3.10 ou superior.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abrir **http://127.0.0.1:5000**. Um banco `cupcakes.db` é criado automaticamente na primeira execução. Alternativamente: `python -m unittest discover -s tests -v` para executar os testes automatizados.

## Fluxo funcional

1. Consultar vitrine e valores.
2. Adicionar itens ao carrinho e ajustar quantidades.
3. Cadastrar usuário ou fazer login.
4. Informar endereço e escolher **pagamento simulado**.
5. Confirmar e consultar histórico de pedidos.

**Aviso:** não há cobrança, integração financeira nem serviço real de entregas. O projeto não deve ser anunciado como loja comercial em produção. Antes de hospedá-lo publicamente, são necessárias melhorias de segurança como token CSRF nos formulários, limite de tentativas de login, configuração HTTPS e `SECRET_KEY` segura.

## Estrutura

`app.py` – rotas (controllers), processamento e persistência SQLite (model); `templates/` – interface (views); `static/` – CSS; `tests/` – testes automatizados; `docs/` – documentação e formulários do trabalho. Arquitetura MVC simplificada, adequada à finalidade didática.

## Publicação e comprovações

A criação do repositório GitHub, a hospedagem pública, os cinco testes independentes e os vídeos narrados dependem da participação do estudante e devem ser preenchidos com informações e evidências reais. Consulte os arquivos na pasta `docs`.
