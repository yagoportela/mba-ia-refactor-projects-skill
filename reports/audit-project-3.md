================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0 + Flask-SQLAlchemy 3.1.1
Files:   11 analyzed | ~1,150 lines of code
Scope:   app.py, database.py, seed.py, models/, routes/, services/, utils/
Date:    2026-11-03

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 6 | LOW: 6
Total: 21 findings

## Findings

### [CRITICAL] Secret key hardcoded
File: app.py:13
Description: `app.config['SECRET_KEY']` está fixo no código com um valor previsível (`super-secret-****`).
Impact: qualquer pessoa com acesso ao repositório pode assinar sessões/tokens; a chave não pode ser rotacionada sem deploy.
Recommendation: mover para variável de ambiente em `config/settings.py`, com `.env.example` e validação no boot.

### [CRITICAL] Hash de senha fraco com MD5
File: models/user.py:27-32
Description: `set_password` e `check_password` usam `hashlib.md5` sem salt.
Impact: senhas quebráveis por rainbow tables e CPU commodity; vazamento de banco expõe credenciais.
Recommendation: usar `werkzeug.security.generate_password_hash/check_password_hash` (scrypt/PBKDF2) ou bcrypt/argon2; migrar hashes no login.

### [CRITICAL] Hash de senha exposto nas respostas da API
File: models/user.py:16-25; routes/user_routes.py:33,85,207-210
Description: `User.to_dict()` inclui o campo `password`; `/users/<id>`, criação de usuário e `/login` retornam esse dicionário.
Impact: qualquer cliente obtém o hash das senhas; facilita quebra offline.
Recommendation: remover `password`/`password_hash` do DTO e criar um DTO público com allowlist de campos.

### [CRITICAL] Credenciais SMTP hardcoded no serviço de notificação
File: services/notification_service.py:7-10
Description: host, porta, usuário e senha do e-mail (`senha****`) estão fixos na classe; o serviço também mantém notificações em memória.
Impact: credenciais expostas e envio de e-mail não configurável/seguro.
Recommendation: mover para env (`SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`), injetar o serviço e não versionar segredos.

### [HIGH] Token fake e ausência de autenticação/autorização
File: routes/user_routes.py:207-211; app.py:18-20
Description: `/login` retorna `'fake-jwt-token-' + user.id` e nenhuma rota valida token; todas as rotas (incluindo deletes e relatórios) são públicas.
Impact: qualquer cliente acessa/edita/exclui dados de qualquer usuário; o "token" não protege nada.
Recommendation: implementar JWT/sessão real, middleware de auth e autorização por papel; nunca aceitar identidade apenas do body.

### [HIGH] Rotas gordas: regra de negócio e validação sem controllers
File: routes/task_routes.py:11-299; routes/user_routes.py:10-211; routes/report_routes.py:12-223
Description: os handlers contêm validação, queries, cálculo de overdue, montagem de DTO e regra de relatório; não existe camada de controllers.
Impact: baixa coesão, duplicação, difícil teste e manutenção.
Recommendation: rotas finas (Blueprints) → controllers de orquestração → services para regra/relatórios → models para persistência.

### [HIGH] Modo debug ligado em todas as interfaces
File: app.py:34
Description: `app.run(debug=True, host='0.0.0.0', port=5000)` expõe o debugger na rede.
Impact: risco de execução remota de código e vazamento de stack traces.
Recommendation: `debug` via env (default `false`), host local em dev e servidor WSGI em produção.

### [HIGH] Exclusão de categoria deixa tasks órfãs
File: routes/report_routes.py:211-223; models/task.py:13-14,20-21
Description: `delete_category` remove a categoria, mas as tasks mantêm `category_id` apontando para um registro inexistente; não há cascade/soft delete.
Impact: dados inconsistentes, relatórios e nomes de categoria quebrados.
Recommendation: definir `ondelete`/cascade, reatribuir tasks para uma categoria padrão ou bloquear a exclusão enquanto houver tasks.

### [HIGH] Tratamento de erros ausente/engolido com `except:` nu
File: routes/task_routes.py:62,137,204,236; routes/user_routes.py:130,150; routes/report_routes.py:186,207,221
Description: vários handlers usam `except:` ou `except Exception` genérico, sem log estruturado nem middleware global; alguns retornam apenas `{'error': 'Erro interno'}`.
Impact: falhas silenciosas, impossível diagnosticar e respostas inconsistentes.
Recommendation: exceções de domínio + `errorhandler` central; logar com contexto e não capturar `BaseException`.

### [MEDIUM] N+1 queries em listagens e relatórios
File: routes/task_routes.py:41-57; routes/user_routes.py:22,35-38,159-181; routes/report_routes.py:53-68,160-164
Description: para cada task busca usuário e categoria; `len(u.tasks)` dispara lazy load por usuário; para cada usuário busca tasks; para cada categoria conta tasks.
Impact: latência cresce linearmente com o volume; sobrecarga no banco.
Recommendation: `joinedload`/`selectinload`, `JOIN` com agregação e `group_by` para contagens.

### [MEDIUM] API deprecated: `datetime.utcnow()`
File: models/task.py:15-16,52; routes/task_routes.py:31,72,215,285; routes/report_routes.py:35,42,45,71,133; seed.py:66-75; utils/helpers.py:38
Description: uso de `datetime.utcnow()`, deprecated a partir do Python 3.12; gera datetimes naive e warnings de deprecação.
Impact: quebra futura em upgrades e inconsistência de timezone.
Recommendation: usar `datetime.now(timezone.utc)` e armazenar/retornar datetimes timezone-aware.

### [MEDIUM] API deprecated: `Query.get()` legado do SQLAlchemy 2.x
File: routes/task_routes.py:42,67,117,122,158,188,195,227; routes/user_routes.py:29,94,136,155; routes/report_routes.py:105,192,213
Description: `Task.query.get(id)`, `User.query.get(id)` e `Category.query.get(id)` usam a API legada de Query, depreciada no SQLAlchemy 2.x.
Impact: warnings de deprecação e risco de remoção em versões futuras.
Recommendation: usar `db.session.get(Model, id)` (ou `db.get_or_404`) em todos os pontos.

### [MEDIUM] Listagens sem paginação
File: routes/task_routes.py:14,266; routes/user_routes.py:12; routes/report_routes.py:159
Description: `Task.query.all()`, `User.query.all()` e `Category.query.all()` retornam todos os registros sem `limit/offset`.
Impact: consumo de memória/latência e risco de resposta enorme.
Recommendation: adicionar `page/per_page` com limite máximo e metadados de paginação.

### [MEDIUM] Validação e serialização duplicadas
File: routes/task_routes.py:16-59; models/task.py:23-36; utils/helpers.py:57-108
Description: a montagem do dicionário de task (incluindo overdue) é repetida em `get_tasks`, `get_task` e `get_user_tasks`; validações de status/prioridade/título estão espalhadas; `process_task_data` existe mas não é usado.
Impact: divergência de comportamento e manutenção custosa.
Recommendation: centralizar serialização no model e validação em `utils/validators.py`, reutilizando em create/update.

### [MEDIUM] CORS totalmente permissivo
File: app.py:15
Description: `CORS(app)` libera qualquer origem sem allowlist.
Impact: sites maliciosos podem chamar a API em nome de usuários.
Recommendation: configurar origens permitidas via env; não usar `*` com credenciais.

### [LOW] Magic numbers/strings
File: routes/task_routes.py:110,113,177,182; routes/report_routes.py:24-28; utils/helpers.py:110-116
Description: listas de status/roles, limites 1–5, 3/200/4 caracteres, cores e `p1..p5` aparecem repetidos e soltos.
Impact: mudanças exigem caça manual e favorecem inconsistência.
Recommendation: constantes nomeadas em `utils/constants.py`/`config`.

### [LOW] Nomenclatura ruim e abreviações
File: routes/report_routes.py:24-28; routes/user_routes.py:14,162; seed.py:66-75
Description: variáveis `p1..p5`, `t`, `u`, `c`, `d`, `cat`, `td` e dicionários `tasks_data` genéricos dificultam a leitura.
Impact: manutenção mais lenta.
Recommendation: nomes intencionais (`prioridade_1`, `task`, `usuario`, `categoria`).

### [LOW] Imports e código mortos
File: app.py:7; routes/task_routes.py:7; routes/user_routes.py:6; routes/report_routes.py:7-8; utils/helpers.py:1-7; services/notification_service.py:1-48
Description: `os`, `sys`, `json`, `time`, `math`, `hashlib` e helpers não usados; `NotificationService` não é instanciado em nenhum lugar.
Impact: ruído, falsa funcionalidade e builds desnecessários.
Recommendation: remover código morto ou integrar o serviço via DI; rodar `ruff`.

### [LOW] Logging improvisado com `print`
File: routes/task_routes.py:149,153,219,234; routes/user_routes.py:83,89,147; utils/helpers.py:39-41; services/notification_service.py:21,24
Description: eventos e erros são impressos com `print`, sem níveis, timestamp estruturado ou correlação.
Impact: operação difícil e risco de vazamento de dados.
Recommendation: logger estruturado com níveis e redaction.

### [LOW] Formato de resposta inconsistente
File: routes/task_routes.py:61,81,150; routes/user_routes.py:25,40,183; routes/report_routes.py:101,155,165
Description: alguns endpoints retornam array direto, outros objeto, outros `{message}`/`{error}`; não há envelope comum.
Impact: clientes precisam de lógica especial; difícil documentar/testar.
Recommendation: padronizar envelope (`data`, `error`, `meta`) e status HTTP.

### [LOW] Senhas fracas nos dados de seed
File: seed.py:19,26,33
Description: usuários de exemplo usam `1234`, `abcd` e `pass`.
Impact: credenciais previsíveis em ambientes de demonstração.
Recommendation: usar senhas fortes geradas/documentadas apenas para dev e nunca reutilizar em produção.

## Deprecated API Scan
- [MEDIUM] `datetime.utcnow()` em models/task.py:15-16,52; routes/task_routes.py:31,72,215,285; routes/report_routes.py:35,42,45,71,133; seed.py:66-75; utils/helpers.py:38 → usar `datetime.now(timezone.utc)`.
- [MEDIUM] `Model.query.get(id)` em routes/task_routes.py:42,67,117,122,158,188,195,227; routes/user_routes.py:29,94,136,155; routes/report_routes.py:105,192,213 → usar `db.session.get(Model, id)`.
- Nenhuma outra API removida/deprecated identificada.

## Endpoint Inventory (baseline para validação)
| Método | Path | Handler | Arquivo:linha |
|---|---|---|---|
| GET | /health | health | app.py:22-24 |
| GET | / | index | app.py:26-28 |
| GET | /tasks | get_tasks | routes/task_routes.py:11-63 |
| GET | /tasks/<int:task_id> | get_task | routes/task_routes.py:65-83 |
| POST | /tasks | create_task | routes/task_routes.py:85-154 |
| PUT | /tasks/<int:task_id> | update_task | routes/task_routes.py:156-223 |
| DELETE | /tasks/<int:task_id> | delete_task | routes/task_routes.py:225-238 |
| GET | /tasks/search | search_tasks | routes/task_routes.py:240-271 |
| GET | /tasks/stats | task_stats | routes/task_routes.py:273-299 |
| GET | /users | get_users | routes/user_routes.py:10-25 |
| GET | /users/<int:user_id> | get_user | routes/user_routes.py:27-40 |
| POST | /users | create_user | routes/user_routes.py:42-90 |
| PUT | /users/<int:user_id> | update_user | routes/user_routes.py:92-132 |
| DELETE | /users/<int:user_id> | delete_user | routes/user_routes.py:134-151 |
| GET | /users/<int:user_id>/tasks | get_user_tasks | routes/user_routes.py:153-183 |
| POST | /login | login | routes/user_routes.py:185-211 |
| GET | /reports/summary | summary_report | routes/report_routes.py:12-101 |
| GET | /reports/user/<int:user_id> | user_report | routes/report_routes.py:103-155 |
| GET | /categories | get_categories | routes/report_routes.py:157-165 |
| POST | /categories | create_category | routes/report_routes.py:167-188 |
| PUT | /categories/<int:cat_id> | update_category | routes/report_routes.py:190-209 |
| DELETE | /categories/<int:cat_id> | delete_category | routes/report_routes.py:211-223 |

## Decision Notes
- O projeto já possui `models/`, `routes/`, `services/` e `utils/`, mas não há controllers e a regra está nas rotas; a refatoração deve evoluir a estrutura, não recriar do zero.
- `NotificationService` não é usado; será mantido como serviço configurável ou removido se não houver caso de uso.
- O endpoint `/login` retorna token fake; a refatoração deve emitir token assinado real ou declarar explicitamente que é um stub de desenvolvimento.
- `seed.py` deve continuar funcionando após a refatoração.

================================
Total: 21 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
