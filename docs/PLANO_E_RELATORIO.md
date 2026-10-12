# PROJETO INTEGRADOR TRANSDISCIPLINAR EM ENGENHARIA DE SOFTWARE II
## Sistema Mobile para Loja Virtual de Cupcakes Gourmet — Doce Encanto

**Instituição:** Universidade Cruzeiro do Sul  
**Estudante:** Flávio Mateus Leme  
**RGM:** [PREENCHER]  
**Situação:** Implementação acadêmica; validação externa pendente.

## 1. Introdução
Este projeto dá continuidade ao PIT em Engenharia de Software I, que realizou o planejamento de uma loja virtual de cupcakes gourmet por meio de histórias de usuário, backlog, modelos UML e proposta de interface. A etapa II concretiza um protótipo web responsivo, com persistência em banco relacional, autenticação, catálogo de produtos, carrinho, finalização de pedidos e visualização de histórico. O pagamento é **simulado**, sem cobrança financeira real.

## 2. Objetivos
**Geral:** implementar e avaliar um sistema web responsivo de loja de cupcakes a partir do projeto elaborado no PIT I.

**Específicos:** revisar modelos e escopo; desenvolver front-end e back-end; implementar projeto físico SQLite; aplicar controles básicos de entrada, sessão e autenticação; preparar testes automatizados e procedimentos de validação com usuários; organizar o código e a documentação para publicação em Git.

## 3. Escopo, premissas e limitações
**Incluído:** catálogo de seis produtos demonstrativos, cadastro, login/logout, carrinho, endereço de entrega, pedido com pagamento demonstrativo e histórico do cliente. **Excluído:** transação financeira real, gestão de estoque, envio de entrega, rastreamento, recuperação de senha e painel administrativo. Os preços são ilustrativos e podem ser alterados no banco.

**Revisões do PIT I:** (a) os wireframes conceituais são convertidos em páginas web responsivas; (b) requisitos de cadastro, compra e consulta de pedidos foram mapeados para rotas; (c) o modelo de classes orientou tabelas relacionais com chaves estrangeiras; (d) foram previstas mensagens de erro, limites de quantidade e senha armazenada sob hash. A arquitetura é **MVC simplificada** em arquivo único: rotas = controlador, SQL = persistência/modelo e Jinja/HTML = visualização. É arquitetura didática, não separação MVC completa em módulos.

## 4. Requisitos implementados
| ID | Requisito | Evidência no código |
|---|---|---|
| RF01 | Exibir catálogo e preço | `GET /` |
| RF02 | Registrar novo cliente | `GET/POST /cadastro` |
| RF03 | Autenticar cliente e encerrar sessão | `GET/POST /entrar`, `POST /sair` |
| RF04 | Adicionar/ajustar/remover itens de carrinho | `POST /carrinho/adicionar/<id>`, `POST /carrinho/atualizar/<id>` |
| RF05 | Informar endereço e forma de pagamento simulada | `GET/POST /finalizar` |
| RF06 | Registrar itens de pedido e histórico | tabelas `orders`, `order_items`, `GET /pedidos` |
| RNF01 | Integridade referencial | `PRAGMA foreign_keys=ON` + FKs |
| RNF02 | Senhas não armazenadas em claro | `generate_password_hash` e `check_password_hash` |
| RNF03 | Responsividade da interface | `static/style.css` |
| RNF04 | Formulários com mensagens de validação | `flash` e verificações de valores |

**Observação:** os requisitos implementados acima podem não cobrir todas as histórias idealizadas no PIT I; o escopo funcional desta entrega está delimitado na seção 3.

## 5. Projeto de dados
**Modelo conceitual:** Usuário (1) — (N) Pedido; Pedido (1) — (N) Item de Pedido; Produto (1) — (N) Item de Pedido. `order_items` preserva preço praticado no pedido, evitando que mudanças de preço afetem o histórico. 

**Modelo lógico relacional:**
- `users(id PK, name, email UNIQUE, password_hash)`
- `products(id PK, name, description, price_cents, emoji, active)`
- `orders(id PK, user_id FK, delivery_address, payment_method, status, total_cents, created_at)`
- `order_items(id PK, order_id FK, product_id FK, quantity, unit_price_cents)`

**Normalização:** os dados de usuário, produto, pedido e item são separados por dependências funcionais; atributos dependem das respectivas chaves. O total do pedido é armazenado como agregado histórico derivável dos itens (redundância intencional para registro comercial), com atualização controlada no checkout. O banco SQLite é criado por `init_db()` no `app.py`.

### Dicionário de dados
| Tabela | Campo | Tipo / restrição | Significado |
|---|---|---|---|
| users | id | INTEGER PK | Identificador do cliente |
| users | name | TEXT NOT NULL | Nome completo |
| users | email | TEXT UNIQUE NOT NULL | Identificação de login |
| users | password_hash | TEXT NOT NULL | Hash da senha |
| products | id | INTEGER PK | Identificador do cupcake |
| products | name | TEXT NOT NULL | Nome comercial |
| products | description | TEXT NOT NULL | Descrição |
| products | price_cents | INTEGER > 0 | Preço em centavos |
| products | emoji | TEXT NOT NULL | Identificador visual |
| products | active | INTEGER default 1 | Disponibilidade |
| orders | id | INTEGER PK | Código do pedido |
| orders | user_id | INTEGER FK | Cliente responsável |
| orders | delivery_address | TEXT NOT NULL | Local de entrega informado |
| orders | payment_method | TEXT NOT NULL | Método **simulado** |
| orders | status | TEXT default Recebido | Estado inicial |
| orders | total_cents | INTEGER >= 0 | Total do pedido em centavos |
| orders | created_at | TEXT CURRENT_TIMESTAMP | Data/hora de registro |
| order_items | id | INTEGER PK | Item do pedido |
| order_items | order_id | INTEGER FK | Pedido relacionado |
| order_items | product_id | INTEGER FK | Produto relacionado |
| order_items | quantity | INTEGER > 0 | Quantidade adquirida |
| order_items | unit_price_cents | INTEGER > 0 | Preço unitário da compra |

## 6. Tecnologias e implementação
**Front-end:** HTML com templates Jinja2 e CSS responsivo. **Back-end:** Python + Flask. **Banco de dados:** SQLite 3. **Plataforma:** web responsiva. **Modalidade:** programação tradicional. **Hospedagem:** não configurada. **Controle de versão:** arquivos preparados para repositório Git; publicação ainda pendente. **Integrações:** nenhuma transação financeira real.

**Fluxo de compra:** cliente abre a vitrine, adiciona produtos ao carrinho, autentica-se, informa endereço e opção demonstrativa de pagamento, confirma pedido, consulta seu histórico. O sistema utiliza sessões HTTP para guardar carrinho e identificador do usuário. Quantidades são limitadas a 30 por produto. 

## 7. Verificação e validação
**Testes automatizados previstos:** catálogo acessível, cadastro duplicado, carrinho com subtotal, pedido persistido, checkout sem autenticação, quantidade inválida, endereço insuficiente e verificação de hash de senha. Arquivo: `tests/test_app.py`. **Status nesta entrega:** código dos testes preparado; a execução depende da instalação das dependências e deve ser registrada com captura da saída do terminal. Não afirmar resultados não verificados.

**Testes com cinco colegas:** os formulários em `TESTES_5_USUARIOS.md` devem ser preenchidos apenas após sessões reais de teste, incluindo nome, data, fluxos exercitados, defeitos encontrados, sugestões e capturas de tela.

## 8. Laudo preliminar de qualidade
| ID | Critério | Situação atual | Ação |
|---|---|---|---|
| Q01 | Verificação estática da sintaxe Python | [registrar execução] | `python -m compileall .` |
| Q02 | Testes automatizados | Pendente de execução documentada | Instalar Flask, executar `unittest` e anexar resultado |
| Q03 | Segurança de produção | Não aprovada | Implementar CSRF, HTTPS, chave secreta forte, limitação de login |
| Q04 | Pagamento e logística reais | Fora do escopo | Manter indicação visível de simulação |
| Q05 | Testes de aceitação com cinco pessoas | Pendente | Coletar avaliações autênticas |
| Q06 | Acessibilidade e UX | Revisão manual pendente | Avaliar contraste, navegação por teclado e feedback |

**Laudo conclusivo:** somente preencher após executar testes e registrar evidências reais, corrigindo defeitos pertinentes.

## 9. Checklist final para entrega
- [ ] Validar o funcionamento no computador e guardar prints da aplicação.
- [ ] Executar testes automatizados e guardar print da saída.
- [ ] Criar repositório GitHub e publicar documentação, código e testes (sem segredos ou banco de clientes).
- [ ] Hospedar aplicação em ambiente apropriado com variáveis de ambiente seguras.
- [ ] Obter e documentar feedback de cinco colegas/profissionais; realizar correções.
- [ ] Registrar antes/depois e elaborar laudo com evidências.
- [ ] Gravar primeiro vídeo narrado de apresentação da implementação (mínimo de cinco minutos, conforme modelo de entrega).
- [ ] Gravar vídeo final da solução atualizada (até cinco minutos).
- [ ] Inserir links reais e RGM no formulário da universidade.

## 10. Conclusão
O projeto converte a concepção da PIT I em artefatos implementados de uma aplicação web responsiva. A avaliação de qualidade final dependerá da execução documentada dos testes, da disponibilização controlada da aplicação e do feedback independente dos avaliadores. Em seu estado atual, representa um **protótipo acadêmico**, e não um produto comercial pronto para operação.

## Referências de suporte
Material da disciplina *Projeto Integrador Transdisciplinar em Engenharia de Software II* (Universidade Cruzeiro do Sul, material fornecido); Projeto Integrador de Engenharia de Software I (documento anterior fornecido); documentação oficial Python, Flask e SQLite, para consulta técnica.
