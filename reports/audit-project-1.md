================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~780 lines of code
Scope:   app.py, controllers.py, models.py, database.py (requirements.txt/README apenas para stack)
Date:    2026-11-03

## Summary
CRITICAL: 5 | HIGH: 5 | MEDIUM: 6 | LOW: 5
Total: 21 findings

## Findings

### [CRITICAL] Hardcoded secret key e modo debug no código
File: app.py:7-8
Description: `SECRET_KEY` fixa (`minha-chave-****`) e `DEBUG = True` configurados diretamente no módulo da aplicação.
Impact: qualquer pessoa com acesso ao repositório pode assinar sessões/tokens; debug em produção expõe o debugger e stack traces.
Recommendation: mover para variáveis de ambiente em `config/settings.py`, com `.env.example`, e manter debug desligado por padrão.

### [CRITICAL] SQL Injection por concatenação de strings
File: models.py:28,48-49,58-60,68,92,110,127-128,140,149-150,155,158-160,164-165,174,188,192,220,224,280,291-297
Description: IDs, nomes, e-mails, senhas, categorias, status e filtros de busca são interpolados diretamente em comandos SQL com `+`/`str()`.
Impact: leitura, escrita e exclusão arbitrária de dados; bypass de login; comprometimento total do SQLite.
Recommendation: usar placeholders (`?`) e parâmetros em todas as queries; montar apenas a estrutura dinâmica do filtro.

### [CRITICAL] Endpoint de execução arbitrária de SQL
File: app.py:59-78
Description: `POST /admin/query` recebe `{"sql": "..."}` do cliente e executa `cursor.execute(query)` sem autenticação nem restrição.
Impact: backdoor completo no banco; permite `DROP TABLE`, exfiltração e alteração de dados.
Recommendation: remover o endpoint ou desativá-lo com 410/403; se necessário, expor operações administrativas específicas, autenticadas e auditadas.

### [CRITICAL] Senhas em texto puro e expostas pela API
File: database.py:76-78; models.py:83,99; controllers.py:130-134,138-144
Description: usuários de seed são gravados com senhas em claro; `get_todos_usuarios`/`get_usuario_por_id` incluem o campo `senha` e os endpoints `/usuarios` e `/usuarios/<id>` o retornam.
Impact: vazamento de credenciais; qualquer cliente lê as senhas de todos os usuários.
Recommendation: armazenar apenas hash forte com salt (`werkzeug.security`) e remover o campo dos DTOs/respostas.

### [CRITICAL] God File / God Method sem separação de responsabilidades
File: models.py:1-314; controllers.py:1-292
Description: `models.py` concentra queries SQL, regra de negócio, serialização e cálculos de quatro domínios; `controllers.py` concentra validação, regra, notificações simuladas e health check.
Impact: impossível testar em isolamento; qualquer mudança afeta vários domínios; alto risco de regressão.
Recommendation: separar por domínio e camada (models, views/routes, controllers, services, middlewares) conforme `mvc-guidelines.md`.

### [HIGH] Regra de negócio e validação pesadas em controllers/rotas
File: controllers.py:24-109,188-255; app.py:11-30
Description: validação de produto, cálculo de pedido, atualização de status e notificações simuladas vivem nos handlers; as rotas são registradas manualmente em `app.py`.
Impact: baixa coesão, duplicação entre criar/atualizar, difícil teste e reuso.
Recommendation: rotas finas (Blueprints) → controllers de orquestração → services para regra/transação → models para persistência.

### [HIGH] Conexão global mutável compartilhada entre threads
File: database.py:4-11
Description: `db_connection` é global e criado uma única vez com `check_same_thread=False`; o schema/seed também são executados nesse singleton.
Impact: condições de corrida, estado compartilhado entre requests/testes e dificuldade de isolar transações.
Recommendation: conexão por request via `flask.g` + `teardown_appcontext`, ou pool de conexões; schema/seed em função de inicialização explícita.

### [HIGH] Endpoints administrativos e dados sensíveis sem autenticação/autorização
File: app.py:47-78; app.py:11-30
Description: `/admin/reset-db` apaga todas as tabelas e `/admin/query` executa SQL, ambos sem token; endpoints de usuários também não têm auth.
Impact: qualquer cliente destrói ou lê dados; não há controle de acesso.
Recommendation: middleware de auth/autorização; `ADMIN_TOKEN` via env e `hmac.compare_digest` para rotas administrativas; proteger dados pessoais.

### [HIGH] Debug ligado em todas as interfaces de rede
File: app.py:8,80-88
Description: `app.run(host="0.0.0.0", port=5000, debug=True)` expõe o servidor na rede com debugger interativo.
Impact: risco de execução remota de código via console de debug e vazamento de stack traces.
Recommendation: `debug` via env (default `false`), host `127.0.0.1` em desenvolvimento e servidor WSGI em produção.

### [HIGH] Criação de pedido sem transação atômica
File: models.py:133-169
Description: o pedido é inserido, depois itens e baixa de estoque são feitos em loops; não há `rollback` se uma etapa falhar após o `INSERT` inicial.
Impact: pedido sem itens, estoque inconsistente e dados parciais em caso de erro.
Recommendation: envolver todo o caso de uso em transação (`BEGIN IMMEDIATE`/`commit`/`rollback`) e validar estoque com `UPDATE ... WHERE estoque >= ?`.

### [MEDIUM] Tratamento de erros duplicado e com vazamento de detalhes internos
File: controllers.py:5-12,21-22,60-62,95-96,108-109,125-126,133-134,143-144,164-165,185-186,218-220,226-227,234-235,254-255,261-262,291-292
Description: cada handler repete `try/except Exception` e devolve `str(e)` ao cliente; não existe middleware global.
Impact: exposição de SQL/stack, respostas inconsistentes e erros silenciosos.
Recommendation: exceções de domínio + `app.errorhandler` central; logar detalhes no servidor e responder mensagem genérica.

### [MEDIUM] N+1 queries na listagem de pedidos
File: models.py:171-201,203-233
Description: para cada pedido, uma query busca itens; para cada item, outra query busca o nome do produto.
Impact: latência cresce linearmente com pedidos/itens; sobrecarga no SQLite.
Recommendation: uma query com `JOIN` entre pedidos/itens/produtos e agrupamento em memória, ou `IN` em lote.

### [MEDIUM] Validação e serialização duplicadas
File: models.py:4-22,24-41,285-314; controllers.py:24-96
Description: o dicionário de produto é repetido em listar/buscar/criar/atualizar; as validações de criar e atualizar são copiadas; listas de status/categorias aparecem em pontos diferentes.
Impact: divergência de comportamento e manutenção custosa.
Recommendation: `to_dict()` no model + validadores/constantes compartilhados no controller/service.

### [MEDIUM] Consultas sem paginação/limite
File: models.py:7,75,206,299
Description: `SELECT *` e listagens retornam todos os registros sem `LIMIT`/paginação.
Impact: consumo de memória e latência; risco de resposta enorme/DoS acidental.
Recommendation: adicionar `page/per_page` (ou `limit/offset`) com limite máximo e metadados de paginação.

### [MEDIUM] Validação ausente em parâmetros de busca e atualização
File: controllers.py:111-126,64-96
Description: `float(preco_min)`/`float(preco_max)` sem `try/except` geram 500; a atualização não valida categoria, tamanho do nome e demais regras usadas na criação.
Impact: 500 inesperado com input inválido e dados inconsistentes via PUT.
Recommendation: validadores centralizados com tipos/ranges e reutilização entre create/update.

### [MEDIUM] CORS totalmente permissivo
File: app.py:9
Description: `CORS(app)` libera qualquer origem sem configuração de allowlist.
Impact: sites maliciosos podem chamar a API em nome de usuários.
Recommendation: configurar origens permitidas via env; não usar `*` com credenciais.

### [LOW] Magic numbers/strings espalhados
File: controllers.py:52,242; models.py:256-262; app.py:82-88
Description: limites de desconto (`10000`, `5000`, `1000`, `0.1`, `0.05`, `0.02`), listas de status/categorias, porta e mensagens ficam soltos no código.
Impact: mudanças exigem caça manual e favorecem inconsistência.
Recommendation: constantes nomeadas em config/domínio.

### [LOW] Nomenclatura ruim e shadowing de built-in
File: models.py:24,43,54,65; controllers.py:37-41,195-196; database.py:5
Description: parâmetros `id` (shadow de built-in), variáveis `db`, `dados`, `e`, `p` e nomes genéricos dificultam leitura.
Impact: manutenção mais lenta e maior chance de erro.
Recommendation: nomes intencionais (`produto_id`, `usuario_id`, `payload`, `erro`) e funções com verbo + objeto.

### [LOW] Imports e código não utilizados
File: database.py:2; models.py:2
Description: `os` em `database.py` e `sqlite3` em `models.py` não são usados; há trechos/constantes sem uso.
Impact: ruído e falsa sensação de dependência.
Recommendation: remover imports mortos e rodar lint (`ruff`/`flake8`).

### [LOW] Logging improvisado com `print`
File: controllers.py:8,11,57,61,106,161,179,182,208-210,219,248,250; app.py:56,83-86
Description: eventos de negócio e erros são impressos com `print`, sem níveis, timestamp ou correlação.
Impact: operação difícil e risco de vazar dados em log.
Recommendation: logger estruturado com níveis e redaction de campos sensíveis.

### [LOW] Formato de resposta inconsistente
File: controllers.py:20,183,206; app.py:64,78
Description: alguns endpoints retornam `{dados, sucesso}`, outros `{erro}`, outros `{erro, sucesso: false}`; há 200 para operações e mensagens em formatos diferentes.
Impact: clientes precisam de lógica especial; difícil documentar/testar.
Recommendation: envelope padronizado (`data`, `error`, `meta`) e status HTTP corretos.

## Deprecated API Scan
- Nenhuma API deprecated encontrada no código-fonte deste projeto.
- Observação: a versão do Flask (3.1.1) e o uso de `add_url_rule`/Blueprints estão atuais.

## Endpoint Inventory (baseline para validação)
| Método | Path | Handler | Arquivo:linha |
|---|---|---|---|
| GET | / | index | app.py:32-45 |
| GET | /produtos | listar_produtos | app.py:11 |
| GET | /produtos/busca | buscar_produtos | app.py:12 |
| GET | /produtos/<int:id> | buscar_produto | app.py:13 |
| POST | /produtos | criar_produto | app.py:14 |
| PUT | /produtos/<int:id> | atualizar_produto | app.py:15 |
| DELETE | /produtos/<int:id> | deletar_produto | app.py:16 |
| GET | /usuarios | listar_usuarios | app.py:18 |
| GET | /usuarios/<int:id> | buscar_usuario | app.py:19 |
| POST | /usuarios | criar_usuario | app.py:20 |
| POST | /login | login | app.py:21 |
| POST | /pedidos | criar_pedido | app.py:23 |
| GET | /pedidos | listar_todos_pedidos | app.py:24 |
| GET | /pedidos/usuario/<int:usuario_id> | listar_pedidos_usuario | app.py:25 |
| PUT | /pedidos/<int:pedido_id>/status | atualizar_status_pedido | app.py:26 |
| GET | /relatorios/vendas | relatorio_vendas | app.py:28 |
| GET | /health | health_check | app.py:30 |
| POST | /admin/reset-db | reset_database | app.py:47 |
| POST | /admin/query | executar_query | app.py:59 |

## Decision Notes
- O projeto não possui testes automatizados; a Fase 3 deve criar um smoke test temporário.
- `database.py` mistura schema, seed e conexão; a refatoração deve separar inicialização de acesso.
- O endpoint `/admin/query` será desativado por segurança (410) e `/admin/reset-db` será protegido por token administrativo.
- Nenhuma API deprecated foi identificada; o scan foi executado mesmo assim.

================================
Total: 21 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
