# Documentação completa — Skill `refactor-arch`

Registro de tudo que foi feito no desafio **Criação de Skills — Refatoração
Arquitetural Automatizada** do módulo *Desenvolvimento de Software e Aplicações
com IA*.

> Guia rápido de execução: [`README.md`](README.md).
> Relatórios de auditoria: [`reports/`](reports/).

**Ferramenta agêntica:** opencode (suporta Skills; a skill também está no path
canônico do Claude Code, `.claude/skills/refactor-arch/`).

**Git:** o código refatorado, a skill e os relatórios já estão commitados. Os
prints de evidência estão no índice (staged) e o `README.md` foi atualizado no
working tree para o commit final.

---

## 1. Resumo executivo

O repositório contém três projetos legados, todos refatorados para o padrão MVC:

| Projeto | Stack | Antes | Depois |
|---|---|---|---|
| `code-smells-project` | Python + Flask 3.1.1 | Monolito de 4 arquivos, SQL Injection, senhas em claro, endpoint de SQL arbitrário | MVC completo com config, models, views, controllers, middlewares, services e utils |
| `ecommerce-api-legacy` | Node.js + Express 4.18.2 | God Class `AppManager`, segredos hardcoded, weak hash, cartão logado, callback hell | Composition root, config, db, models, services, controllers, routes, middlewares e utils |
| `task-manager-api` | Python + Flask 3.0.0 + Flask-SQLAlchemy | MVC parcial, rotas gordas, MD5, senha exposta, fake JWT, APIs deprecated | Controllers, config, middlewares, services, rotas finas, hash forte e APIs modernas |

A skill `refactor-arch` foi criada com três fases (Análise, Auditoria e
Refatoração), 7 arquivos Markdown (SKILL.md + 6 referências) e copiada
integralmente para os três projetos. Foram gerados 3 relatórios com 21 findings
cada (63 no total).

Validação final:

- Projeto 1: 35 requisições, 19 endpoints, boot real com health `200`.
- Projeto 2: 20 checks, 3 endpoints, boot real com health `200`.
- Projeto 3: 31 requisições, 22 endpoints, auth opcional, boot real com health `200`.

---

## 2. Linha do tempo do que foi feito

1. **Leitura dos três projetos** e entendimento de stack, domínio, arquitetura e
   problemas intencionais.
2. **Análise manual** de cada projeto, com pelo menos 5 problemas documentados e
   classificação CRITICAL/HIGH/MEDIUM/LOW.
3. **Criação da skill** em `code-smells-project/.claude/skills/refactor-arch/`:
   `SKILL.md` + referências de análise, anti-patterns, template, MVC, playbook e
   validação.
4. **Integração com opencode**: `opencode.json` com `skills.paths` apontando para
   `.claude/skills`; comandos `/refactor-arch` em `.opencode/command/` e
   `.claude/commands/`.
5. **Cópia da skill** para `ecommerce-api-legacy/` e `task-manager-api/`.
6. **Geração dos relatórios** `reports/audit-project-1.md`,
   `audit-project-2.md` e `audit-project-3.md` a partir do código original.
7. **Refatoração do Projeto 1** (`code-smells-project`): configuração por env,
   models/views/controllers por domínio, SQL parametrizado, hash de senha, auth
   admin, transações, JOIN para pedidos, paginação e error handling central.
8. **Refatoração do Projeto 2** (`ecommerce-api-legacy`): quebra da God Class,
   config por env, scrypt, validação, transações, DI, async/await, relatório com
   JOIN, cascade e auth admin opcional.
9. **Refatoração do Projeto 3** (`task-manager-api`): app factory, controllers,
   middlewares, services, validadores, hash forte, DTO sem senha, token assinado,
   agregações, paginação, substituição de `utcnow()`/`Query.get()` e correção de
   categoria órfã.
10. **Validação** com smoke tests temporários e boot real dos três apps.
11. **Documentação**: README de execução, READMEs dos projetos, relatórios e este
    `doc.md`.
12. **Git:** código refatorado, skill e relatórios commitados; prints de evidência
    adicionados ao índice e `README.md` atualizado no working tree.

---

## 3. Inventário de arquivos criados/alterados

### 3.1 Raiz do repositório

| Arquivo | O que é |
|---|---|
| `README.md` | Guia de execução (pré-requisitos, comandos, validação) |
| `doc.md` | Este documento completo |
| `reports/audit-project-1.md` | Auditoria original do Projeto 1 (21 findings) |
| `reports/audit-project-2.md` | Auditoria original do Projeto 2 (21 findings) |
| `reports/audit-project-3.md` | Auditoria original do Projeto 3 (21 findings) |
| `.gitignore` | Mantido: ignora `.env`, `.venv`, `node_modules`, `*.db`, `instance/` |

### 3.2 Skill (idêntica nos 3 projetos)

```text
<projeto>/.claude/skills/refactor-arch/
├── SKILL.md
└── references/
    ├── project-analysis.md
    ├── anti-patterns.md
    ├── report-template.md
    ├── mvc-guidelines.md
    ├── refactoring-playbook.md
    └── validation.md
```

Também em cada projeto:

```text
<projeto>/opencode.json
<projeto>/.opencode/command/refactor-arch.md
<projeto>/.claude/commands/refactor-arch.md
```

### 3.3 Projeto 1 — `code-smells-project`

**Criados:**

```text
config/settings.py
models/{produto_model,usuario_model,pedido_model,relatorio_model,health_model}.py
views/{produto_routes,usuario_routes,pedido_routes,relatorio_routes,health_routes,index_routes,admin_routes}.py
controllers/{produto_controller,usuario_controller,pedido_controller,relatorio_controller,health_controller,admin_controller}.py
middlewares/{error_handler,auth}.py
services/{auth_service,notification_service}.py
utils/{constants,errors,validators}.py
app.py (reescrito como app factory/composition root)
database.py (reescrito: conexão por request, schema e seed com hash)
.env.example
```

**Removidos:** `controllers.py`, `models.py` (substituídos pelas pastas
`controllers/` e `models/`).

### 3.4 Projeto 2 — `ecommerce-api-legacy`

**Criados:**

```text
src/config/index.js
src/db/database.js
src/models/{userModel,courseModel,enrollmentModel,paymentModel,auditLogModel,reportModel}.js
src/services/{checkoutService,reportService,userService,paymentService,cacheService}.js
src/controllers/{checkoutController,reportController,userController}.js
src/routes/{index,checkoutRoutes,reportRoutes,userRoutes}.js
src/middlewares/{asyncHandler,errorHandler,auth}.js
src/utils/{errors,logger,password,validators}.js
app.js (reescrito como composition root)
.env.example
api.http (atualizado)
```

**Removidos:** `src/AppManager.js`, `src/utils.js`.

### 3.5 Projeto 3 — `task-manager-api`

**Criados:**

```text
config/settings.py
controllers/{task_controller,user_controller,category_controller,report_controller}.py
middlewares/{error_handler,auth}.py
routes/category_routes.py
routes/health_routes.py
services/{auth_service,report_service}.py
utils/{constants,datetime_utils,errors,validators}.py
.env.example
app.py (reescrito como app factory/composition root)
seed.py (reescrito com hash forte e utcnow moderno)
```

**Alterados:** `models/task.py`, `models/user.py`, `models/category.py`,
`routes/task_routes.py`, `routes/user_routes.py`, `routes/report_routes.py`,
`routes/__init__.py`, `services/notification_service.py`, `requirements.txt`.

**Removidos:** `utils/helpers.py`.

**Observação:** em 2026-11-03, `ApiError` foi movido de `middlewares/errors.py`
para `utils/errors.py` nos Projetos 1 e 3, para que models/services não dependam
da camada de middlewares.

### 3.6 Artefatos de ambiente (não versionados)

- `.venv/` criado nos Projetos 1 e 3 para instalar as dependências e validar o
  boot; ignorado pelo `.gitignore`.
- `node_modules/` criado no Projeto 2 via `npm install`; ignorado.
- `loja.db` e `tasks.db` são bancos SQLite gerados em runtime; ignorados por
  `*.db`.
- `package-lock.json` do Projeto 2 pode ter sido atualizado pelo `npm install`.
- Smoke tests e logs de boot foram executados em arquivos temporários fora do
  repositório (`%TEMP%/opencode/`), para não poluir o projeto.

---

## 4. Análise Manual

A análise foi feita **antes** da refatoração, lendo o código-fonte e registrando
arquivo/linha. Os relatórios completos estão em `reports/`.

### 4.1 `code-smells-project` (Python/Flask — E-commerce)

**Stack detectada:** Python 3 + Flask 3.1.1, Flask-CORS 5.0.1, SQLite (`loja.db`).
**Arquitetura original:** monolito em 4 arquivos (`app.py`, `controllers.py`,
`models.py`, `database.py`), sem separação de camadas.
**Domínio:** catálogo de produtos, usuários, pedidos, estoque e relatório de vendas.

| Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|
| CRITICAL | `SECRET_KEY` e `DEBUG` hardcoded | `app.py:7-8` | Qualquer pessoa com acesso ao código assina sessões; debug ligado expõe o debugger. |
| CRITICAL | SQL Injection por concatenação | `models.py:28,48-49,58-60,68,92,110,127-128,140,149-150,155,158-160,164-165,174,188,192,220,224,280,291-297` | Inputs de rota e body entram diretamente no SQL; permite leitura, escrita e exclusão arbitrária. |
| CRITICAL | Execução arbitrária de SQL | `app.py:59-78` | `POST /admin/query` executa o SQL enviado pelo cliente sem auth; backdoor completo. |
| CRITICAL | Senhas em texto puro e expostas | `database.py:76-78`; `models.py:83,99`; `controllers.py:130-144` | Seed grava senhas em claro e `/usuarios` devolve o campo `senha`. |
| CRITICAL | God File / God Method | `models.py:1-314`; `controllers.py:1-292` | Quatro domínios, SQL, validação, regra e serialização concentrados; impossível testar em isolamento. |
| HIGH | Conexão global mutável | `database.py:4-11` | `db_connection` global com `check_same_thread=False` gera condição de corrida e estado compartilhado. |
| HIGH | Debug em `0.0.0.0` | `app.py:8,80-88` | Servidor exposto na rede com debugger interativo. |
| HIGH | Pedido sem transação | `models.py:133-169` | Pedido pode ser criado sem itens/estoque consistente se uma etapa falhar. |
| MEDIUM | N+1 queries em pedidos | `models.py:171-201,203-233` | Para cada pedido busca itens; para cada item busca produto. |
| MEDIUM | Consultas sem paginação | `models.py:7,75,206,299` | `SELECT *` e listagens sem `LIMIT` crescem sem controle. |
| LOW | Magic numbers/strings | `controllers.py:52,242`; `models.py:256-262` | Limites de desconto, status, categorias e portas soltos no código. |
| LOW | Nomenclatura/imports mortos | `database.py:2`; `models.py:2`; `models.py:24,43,54,65` | `id` como parâmetro (shadow), `db`, `dados`, `e`, `p`; imports sem uso. |

### 4.2 `ecommerce-api-legacy` (Node.js/Express — LMS com checkout)

**Stack detectada:** Node.js + Express 4.18.2, `sqlite3` 5.1.6, banco em memória.
**Arquitetura original:** `src/app.js` + `src/AppManager.js` + `src/utils.js`; uma
God Class inicializa banco, registra rotas, processa checkout e gera relatório.
**Domínio:** LMS: usuários, cursos, matrículas, pagamentos e auditoria.

| Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|
| CRITICAL | Credenciais/chaves hardcoded | `src/utils.js:1-7` | `dbPass`, `paymentGatewayKey` (`pk_live_****`) e SMTP no código. |
| CRITICAL | Weak hash e senha de seed em claro | `src/utils.js:17-23`; `src/AppManager.js:18` | `badCrypto` concatena base64; seed usa uma senha de 3 dígitos. |
| CRITICAL | Cartão e chave do gateway em log | `src/AppManager.js:45` | Vazamento de dados de cartão (PCI) e chave de pagamento. |
| CRITICAL | God Class `AppManager` | `src/AppManager.js:1-141` | Banco, rotas, negócio, relatório e exclusão no mesmo lugar. |
| CRITICAL | Bypass de autenticação no checkout | `src/AppManager.js:40-75` | Usuário existente é aceito sem validar a senha informada. |
| HIGH | Checkout sem transação | `src/AppManager.js:50-63` | Matrícula/pagamento/auditoria podem ficar parcialmente gravados. |
| HIGH | Callback hell + negócio na rota | `src/AppManager.js:28-78,80-129` | 4+ níveis de callbacks, difícil testar e tratar erro. |
| HIGH | Estado global mutável | `src/utils.js:9-15` | `globalCache` e `totalRevenue` exportados e mutáveis. |
| MEDIUM | N+1 no relatório financeiro | `src/AppManager.js:89-127` | Para cada curso busca matrículas; para cada matrícula usuário/pagamento. |
| MEDIUM | Validação fraca | `src/AppManager.js:29-35,46` | Sem validação de e-mail; cartão validado só por prefixo `4`. |
| LOW | Magic numbers/strings | `src/utils.js:19-22`; `src/AppManager.js:46,57` | `10000`, `substring(0,10)`, `"PAID"`, `"4"`. |
| LOW | Nomenclatura ruim | `src/AppManager.js:29-33,89-127` | `u`, `e`, `p`, `cid`, `cc`, `enr`, `c`. |

### 4.3 `task-manager-api` (Python/Flask — Task Manager)

**Stack detectada:** Python 3 + Flask 3.0.0, Flask-SQLAlchemy 3.1.1, SQLite.
**Arquitetura original:** MVC parcial — já existiam `models/`, `routes/`,
`services/` e `utils/`, mas não havia controllers e a regra estava nas rotas.
**Domínio:** tarefas, usuários, categorias, prazos e relatórios de produtividade.

| Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|
| CRITICAL | `SECRET_KEY` hardcoded | `app.py:13` | Chave fixa no repositório; não pode ser rotacionada sem deploy. |
| CRITICAL | Senhas com MD5 sem salt | `models/user.py:27-32` | Hash quebrável por rainbow tables. |
| CRITICAL | Hash de senha exposto na API | `models/user.py:16-25`; `routes/user_routes.py:33,85,207-210` | `/users`, criação e login devolvem `password`. |
| CRITICAL | Credenciais SMTP hardcoded | `services/notification_service.py:7-10` | Usuário/senha de e-mail no código. |
| HIGH | Rotas gordas sem controllers | `routes/task_routes.py:11-299`; `routes/user_routes.py:10-211`; `routes/report_routes.py:12-223` | Validação, queries, regra e serialização nos handlers. |
| HIGH | Fake JWT e ausência de auth | `routes/user_routes.py:207-211`; `app.py:18-20` | Token `fake-jwt-token-<id>` não protege nenhuma rota. |
| MEDIUM | N+1 em listagens/relatórios | `routes/task_routes.py:41-57`; `routes/user_routes.py:22,35-38,159-181`; `routes/report_routes.py:53-68,160-164` | Lazy load por usuário/categoria e loops de contagem. |
| MEDIUM | API deprecated `datetime.utcnow()` | `models/task.py:15-16,52`; `routes/task_routes.py:31,72,215,285`; `routes/report_routes.py:35,42,45,71,133`; `seed.py:66-75`; `utils/helpers.py:38` | Deprecated no Python 3.12; gera datas naive. |
| MEDIUM | API deprecated `Query.get()` | `routes/task_routes.py:42,67,117,122,158,188,195,227`; `routes/user_routes.py:29,94,136,155`; `routes/report_routes.py:105,192,213` | API legada do SQLAlchemy 2.x. |
| MEDIUM | Listagens sem paginação | `routes/task_routes.py:14,266`; `routes/user_routes.py:12`; `routes/report_routes.py:159` | `.all()` sem limite. |
| LOW | Magic numbers/strings | `routes/task_routes.py:110,113,177,182`; `routes/report_routes.py:24-28`; `utils/helpers.py:110-116` | Status, prioridade, limites e cores repetidos. |
| LOW | Código morto | `app.py:7`; `routes/task_routes.py:7`; `utils/helpers.py:1-7`; `services/notification_service.py` | Imports/helpers não usados e serviço nunca instanciado. |

---

## 5. Construção da Skill

### 5.1 Estrutura

```text
<projeto>/.claude/skills/refactor-arch/
├── SKILL.md
└── references/
    ├── project-analysis.md
    ├── anti-patterns.md
    ├── report-template.md
    ├── mvc-guidelines.md
    ├── refactoring-playbook.md
    └── validation.md
```

Além da skill, cada projeto recebeu `opencode.json`,
`.opencode/command/refactor-arch.md` e `.claude/commands/refactor-arch.md`.

### 5.2 Decisões de design do `SKILL.md`

- **Três fases sequenciais:** Análise → Auditoria → Refatoração.
- **Gate humano:** a Fase 2 termina com
  `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]`; nenhum arquivo
  de código é alterado antes do `y`.
- **Saídas padronizadas:** blocos fixos para as Fases 1 e 3.
- **Evidência obrigatória:** todo finding precisa de `arquivo:linha`.
- **Preservação de contrato:** paths, métodos e formato essencial das respostas
  são mantidos; mudanças de segurança são registradas.
- **Segurança no prompt:** não reproduzir segredos, não executar SQL arbitrário,
  não usar git sem pedido.
- **Referências como conhecimento de domínio:** o `SKILL.md` é o "quê/como"; os
  arquivos em `references/` são o conhecimento especializado.

### 5.3 Referências e áreas de conhecimento

| Arquivo | Área obrigatória | Conteúdo |
|---|---|---|
| `project-analysis.md` | Análise de projeto | Heurísticas de linguagem/framework/banco/domínio, mapeamento de arquitetura, inventário de endpoints, contagem de LOC, comandos de boot. |
| `anti-patterns.md` | Catálogo de anti-patterns | 25 anti-patterns com sinais acionáveis, severidade, impacto, recomendação e tabela de APIs deprecated. |
| `report-template.md` | Template de relatório | Estrutura exata da Fase 2, summary, findings, deprecated scan, endpoint inventory e confirmação. |
| `mvc-guidelines.md` | Guidelines de arquitetura | Responsabilidades de Model, View/Routes, Controller, Service, Middleware, Config e composition root; exemplos Flask/Express; checklist. |
| `refactoring-playbook.md` | Playbook de refatoração | 15 padrões de transformação com antes/depois (P1–P15). |
| `validation.md` | Validação (extra) | Checklist de checagem estática, boot, smoke test de endpoints, re-auditoria e critérios de aceite. |

### 5.4 Catálogo de anti-patterns

O catálogo tem **25 anti-patterns** distribuídos em todas as severidades:

- **CRITICAL (6):** credenciais hardcoded; SQL/NoSQL injection; God Class/File;
  execução arbitrária de SQL; senha em texto puro/weak hash; exposição de dados
  sensíveis em respostas/logs.
- **HIGH (6):** lógica pesada em rotas/controllers; estado global mutável;
  acoplamento sem DI; escrita sem transação; ausência de auth em rotas sensíveis;
  callback hell.
- **MEDIUM (7):** N+1; validação ausente; duplicação; erros engolidos/vazando;
  falta de paginação; APIs deprecated; CORS permissivo.
- **LOW (6):** nomenclatura ruim; magic numbers/strings; código morto; logs com
  `print`/`console.log`; respostas inconsistentes; falta de testes/documentação.

**Por que esses?** São os padrões presentes nos três projetos e os de maior
impacto arquitetural/segurança. O catálogo prioriza sinais de detecção acionáveis
(ex.: "query dentro de `for`", "senha em `to_dict`", "`SELECT` sem `LIMIT`").

### 5.5 Detecção de APIs deprecated

| Deprecated | Equivalente moderno |
|---|---|
| `datetime.utcnow()` | `datetime.now(timezone.utc)` |
| `Model.query.get(id)` (SQLAlchemy 2.x) | `db.session.get(Model, id)` |
| `flask.ext.*` | imports diretos |
| `@app.before_first_request` | inicialização no factory |
| `new Buffer(data)` | `Buffer.from(data)` |
| `url.parse()` | `new URL()` |
| `crypto.createCipher` | `crypto.createCipheriv` |
| `res.sendfile()` | `res.sendFile()` |
| `body-parser` | `express.json()` |
| callbacks do Mongoose v7+ | Promises/async-await |

No Projeto 3, `datetime.utcnow()` e `Query.get()` foram detectados e
substituídos. No Projeto 2, o scan não achou API deprecated no código-fonte, mas
registrou dependências transitivas deprecated e vulneráveis do `npm`.

### 5.6 Playbook

O playbook tem **15 transformações** com exemplos antes/depois:

P1 config/segredos para env · P2 queries parametrizadas · P3 quebrar God
Class/File · P4 rotas finas + controllers · P5 erro centralizado · P6 eliminar
N+1 · P7 hash forte de senha · P8 transações · P9 remover estado global/DI ·
P10 validação centralizada · P11 remover dados sensíveis · P12 substituir APIs
deprecated · P13 paginação · P14 async/await · P15 restringir endpoints perigosos.

### 5.7 Como a skill é agnóstica de tecnologia

1. A Fase 1 procura manifests (`package.json`, `requirements.txt`, etc.),
   imports e padrões de bootstrap.
2. O alvo MVC é descrito por responsabilidades, não por pastas fixas; há exemplos
   para Flask e Express e a regra "evolua, não reescreva" para projetos já
   organizados.
3. O playbook mostra as mesmas transformações em Python e JavaScript.
4. A validação é genérica: boot + smoke test dos endpoints inventariados.
5. A skill não contém nomes de projetos, caminhos absolutos ou regras específicas
   de um dos três repositórios; a mesma cópia foi usada nos três.
6. O catálogo de APIs deprecated cobre Python/Flask/SQLAlchemy e Node/Express.

### 5.8 Integração com opencode

Cada projeto tem:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "skills": {
    "paths": [".claude/skills"]
  }
}
```

Assim, a skill fica no path canônico `.claude/skills/refactor-arch/` e é
carregada pelo opencode. Os comandos `/refactor-arch` estão em
`.opencode/command/refactor-arch.md` e `.claude/commands/refactor-arch.md`.

### 5.9 Desafios e soluções

| Desafio | Solução |
|---|---|
| Preservar contratos HTTP ao corrigir segurança | Rotas mantidas; `/admin/query` do Projeto 1 responde 410; `/admin/reset-db` exige token; auth admin do Projeto 2 é opt-in via `ADMIN_TOKEN`; Projeto 3 tem `AUTH_REQUIRED` configurável. |
| Projeto 2 com callbacks e transações | `Database` com wrappers Promise, fila de transações e `async/await`; checkout inteiro em transação. |
| Projeto 3 já parcialmente organizado | Extração incremental: controllers, config, middleware e validators, sem recriar models/services existentes. |
| Datas deprecated sem quebrar SQLite | Helper `utcnow()` usa `datetime.now(timezone.utc)` e remove o `tzinfo` para manter compatibilidade com colunas `DateTime` existentes. |
| N+1 em relatórios | JOIN/`group_by`/`joinedload`; uma query para o relatório financeiro e agregações para os relatórios do Task Manager. |
| CORS e segredos | Config via env; CORS restrito por allowlist; `.env.example` em todos os projetos. |
| Node com `sqlite3` nativo | `npm install` validado; o módulo `sqlite3` carregou corretamente no ambiente. |
| Validação real | Smoke tests temporários com 35, 20 e 31 requisições, além de boot real de cada aplicação. |

---

## 6. Resultados

### 6.1 Resumo dos relatórios

| Projeto | Stack | Fase 1 | Findings | Endpoints | Validação |
|---|---|---|---|---|---|
| `code-smells-project` | Python + Flask 3.1.1 | 4 arquivos, ~780 LOC, monolito, SQLite | C 5 · H 5 · M 6 · L 5 = **21** | 19 | 35 requisições + boot real |
| `ecommerce-api-legacy` | Node.js + Express 4.18.2 | 3 arquivos, ~180 LOC, God Class, SQLite em memória | C 5 · H 6 · M 5 · L 5 = **21** | 3 | 20 checks + boot real |
| `task-manager-api` | Python + Flask 3.0.0 + Flask-SQLAlchemy 3.1.1 | 11 arquivos, ~1,150 LOC, MVC parcial, SQLite | C 4 · H 5 · M 6 · L 6 = **21** | 22 | 31 requisições + auth + boot real |

Relatórios completos: [`reports/audit-project-1.md`](reports/audit-project-1.md),
[`reports/audit-project-2.md`](reports/audit-project-2.md),
[`reports/audit-project-3.md`](reports/audit-project-3.md).

### 6.2 Antes/depois da estrutura

#### Projeto 1 — `code-smells-project`

**Antes**

```text
code-smells-project/
├── app.py             # rotas + admin perigoso + debug
├── controllers.py     # validação + regra + notificações
├── models.py          # SQL + regra + serialização (4 domínios)
├── database.py        # conexão global + schema + seed
└── requirements.txt
```

**Depois**

```text
code-smells-project/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   ├── usuario_model.py
│   ├── pedido_model.py
│   ├── relatorio_model.py
│   └── health_model.py
├── views/
│   ├── produto_routes.py
│   ├── usuario_routes.py
│   ├── pedido_routes.py
│   ├── relatorio_routes.py
│   ├── health_routes.py
│   ├── index_routes.py
│   └── admin_routes.py
├── controllers/
│   ├── produto_controller.py
│   ├── usuario_controller.py
│   ├── pedido_controller.py
│   ├── relatorio_controller.py
│   ├── health_controller.py
│   └── admin_controller.py
├── middlewares/
│   ├── error_handler.py
│   └── auth.py
├── services/
│   ├── auth_service.py
│   └── notification_service.py
├── utils/
│   ├── constants.py
│   ├── errors.py
│   └── validators.py
├── database.py
├── app.py               # composition root
├── .env.example
└── requirements.txt
```

#### Projeto 2 — `ecommerce-api-legacy`

**Antes**

```text
ecommerce-api-legacy/
└── src/
    ├── app.js
    ├── AppManager.js   # God Class
    └── utils.js        # segredos + cache global + weak hash
```

**Depois**

```text
ecommerce-api-legacy/
├── src/
│   ├── app.js                    # composition root
│   ├── config/index.js
│   ├── db/database.js
│   ├── models/
│   │   ├── userModel.js
│   │   ├── courseModel.js
│   │   ├── enrollmentModel.js
│   │   ├── paymentModel.js
│   │   ├── auditLogModel.js
│   │   └── reportModel.js
│   ├── services/
│   │   ├── checkoutService.js
│   │   ├── reportService.js
│   │   ├── userService.js
│   │   ├── paymentService.js
│   │   └── cacheService.js
│   ├── controllers/
│   │   ├── checkoutController.js
│   │   ├── reportController.js
│   │   └── userController.js
│   ├── routes/
│   │   ├── index.js
│   │   ├── checkoutRoutes.js
│   │   ├── reportRoutes.js
│   │   └── userRoutes.js
│   ├── middlewares/
│   │   ├── asyncHandler.js
│   │   ├── errorHandler.js
│   │   └── auth.js
│   └── utils/
│       ├── errors.js
│       ├── logger.js
│       ├── password.js
│       └── validators.js
├── .env.example
├── api.http
├── package.json
└── README.md
```

#### Projeto 3 — `task-manager-api`

**Antes**

```text
task-manager-api/
├── app.py             # secret hardcoded + debug + rotas soltas
├── database.py
├── seed.py
├── models/            # Task/User/Category (MD5, senha exposta)
├── routes/            # handlers gordos
├── services/          # NotificationService com SMTP hardcoded
└── utils/             # helpers duplicados/não usados
```

**Depois**

```text
task-manager-api/
├── app.py                    # app factory + composition root
├── database.py               # SQLAlchemy db
├── seed.py                   # seed com hash forte + utcnow moderno
├── config/settings.py
├── controllers/
│   ├── task_controller.py
│   ├── user_controller.py
│   ├── category_controller.py
│   └── report_controller.py
├── middlewares/
│   ├── error_handler.py
│   └── auth.py
├── models/
│   ├── task.py
│   ├── user.py
│   └── category.py
├── routes/                   # Views/Routes finas
│   ├── task_routes.py
│   ├── user_routes.py
│   ├── category_routes.py
│   ├── report_routes.py
│   └── health_routes.py
├── services/
│   ├── auth_service.py
│   ├── notification_service.py
│   └── report_service.py
├── utils/
│   ├── constants.py
│   ├── datetime_utils.py
│   ├── errors.py
│   └── validators.py
├── .env.example
└── requirements.txt
```

### 6.3 Checklist de validação

| Critério | Projeto 1 | Projeto 2 | Projeto 3 |
|---|---|---|---|
| Linguagem detectada corretamente | ✅ Python | ✅ JavaScript/Node | ✅ Python |
| Framework detectado corretamente | ✅ Flask 3.1.1 | ✅ Express 4.18.2 | ✅ Flask 3.0.0 |
| Domínio descrito corretamente | ✅ E-commerce | ✅ LMS/checkout | ✅ Task Manager |
| Nº de arquivos condiz com a realidade | ✅ 4 | ✅ 3 | ✅ 11 |
| Relatório segue o template | ✅ | ✅ | ✅ |
| Cada finding tem arquivo/linha | ✅ | ✅ | ✅ |
| Findings ordenados CRITICAL → LOW | ✅ | ✅ | ✅ |
| Mínimo de 5 findings | ✅ 21 | ✅ 21 | ✅ 21 |
| Deprecated APIs (se aplicável) | ✅ nenhum no source | ✅ deps transitivas/vulns | ✅ `utcnow` + `Query.get` |
| Pausa/confirmação antes da Fase 3 | ✅ | ✅ | ✅ |
| Estrutura de diretórios MVC | ✅ | ✅ | ✅ |
| Configuração em módulo (sem hardcoded) | ✅ | ✅ | ✅ |
| Models abstraem dados | ✅ | ✅ | ✅ |
| Views/Routes separadas | ✅ | ✅ | ✅ |
| Controllers concentram o fluxo | ✅ | ✅ | ✅ |
| Error handling centralizado | ✅ | ✅ | ✅ |
| Entry point claro | ✅ | ✅ | ✅ |
| Aplicação inicia sem erros | ✅ | ✅ | ✅ |
| Endpoints originais respondem | ✅ 19/19* | ✅ 3/3 | ✅ 22/22 |

\* No Projeto 1, `POST /admin/query` foi desativado por segurança e responde
`410 Gone`; `POST /admin/reset-db` exige `X-Admin-Token`. No Projeto 2, as rotas
admin exigem token apenas se `ADMIN_TOKEN` estiver definido. No Projeto 3,
`AUTH_REQUIRED=false` por padrão; com `true`, todas as rotas exceto `/`,
`/health` e `/login` exigem Bearer token.

### 6.4 Logs das aplicações rodando após a refatoração

#### Projeto 1 — boot e endpoints

```text
--- stdout ---
 * Serving Flask app 'app'
 * Debug mode: off
--- stderr ---
2026-11-03 22:15:14,213 INFO werkzeug WARNING: This is a development server. ...
 * Running on http://127.0.0.1:5001
health: 200 {"counts":{"pedidos":0,"produtos":10,"usuarios":3},"database":"connected","status":"ok","versao":"1.0.0"}
produtos: 200
...
OK: 35 requests validated
```

#### Projeto 2 — boot e endpoints

```text
{"timestamp":"2026-11-04T01:17:26.015Z","level":"info","message":"Frankenstein LMS rodando","meta":{"port":3000,"database":":memory:"}}
health: 200 {"status":"ok"}
report: 200 [{"course":"Clean Architecture","revenue":997,"students":[{"student":"Leonan","paid":997}]},{"course":"Docker","revenue":0,"students":[]}]
...
OK: 20 checks passed
```

#### Projeto 3 — boot e endpoints

```text
 * Serving Flask app 'app'
 * Debug mode: off
2026-11-03 22:24:17,494 INFO werkzeug WARNING: ...
 * Running on http://127.0.0.1:5002
health: 200 {"status":"ok","timestamp":"2026-11-04T01:24:21.081540+00:00"}
tasks: 200 count=10
summary: 200
login: 200 token=True userHasPassword=False
...
OK: 31 requests validated + auth middleware
```

### 6.5 Observações por stack

- **Projeto 1 (monolito Python/Flask):** a skill aplicou o conjunto completo de
  transformações (P1–P15), separou 4 domínios e eliminou SQL Injection, senha em
  claro, endpoint de SQL arbitrário e estado global. Foi o caso de maior esforço
  estrutural.
- **Projeto 2 (Node/Express):** a skill adaptou o playbook para callbacks →
  Promises/async-await, transações serializadas, DI no composition root e uma
  única query para o relatório. O comportamento de simulação de pagamento por
  prefixo do cartão foi preservado, mas sem logar cartão/chave.
- **Projeto 3 (Flask já organizado):** a skill não recriou a estrutura; adicionou
  controllers/config/middlewares, moveu regra das rotas para services, corrigiu
  segurança e substituiu APIs deprecated. Isso comprova a regra "evoluir, não
  reescrever".

### 6.6 Riscos residuais

A Fase 3 eliminou todos os CRITICAL dos três projetos. Alguns itens de severidade
HIGH/MEDIUM permanecem **por decisão de escopo**:

- **Projeto 1 — HIGH residual (auth de negócio):** endpoints de negócio continuam
  públicos porque o original não tinha fluxo de login/autorização. As rotas
  administrativas foram protegidas: `/admin/query` responde 410 e
  `/admin/reset-db` exige `X-Admin-Token`. Senhas de seed são de demonstração
  (agora hasheadas).
- **Projeto 2 — HIGH residual (dependências):** a auth admin é opt-in
  (`ADMIN_TOKEN`); o banco default é `:memory:`; o pagamento é uma simulação por
  prefixo do cartão. O `npm audit` ainda reporta 17 vulnerabilidades (2 critical,
  8 high) em dependências transitivas; não atualizamos para evitar quebra de
  compatibilidade neste desafio. Recomenda-se `npm audit fix`/upgrade com testes.
- **Projeto 3 — HIGH residual (auth opcional):** `AUTH_REQUIRED=false` por
  padrão; quando `true`, todas as rotas (exceto `/`, `/health` e `/login`) exigem
  Bearer token. Senhas de seed são fracas (embora agora hasheadas); SMTP fica
  desabilitado se não configurado. Se existir um `tasks.db` antigo com MD5, rode
  `python seed.py` para recriar os usuários.

---

## 7. Como executar (resumo)

O guia detalhado está no [`README.md`](README.md). Resumo:

### 7.1 Pré-requisitos

- opencode (ferramenta escolhida) ou Claude Code.
- Python 3.12+ e `pip`.
- Node.js 20+ e `npm`.
- Reinicie o opencode após carregar/alterar a skill.

### 7.2 Invocar a skill

```bash
cd code-smells-project
opencode
/refactor-arch
```

A skill executa as três fases e para na Fase 2 pedindo confirmação. Para Claude
Code:

```bash
claude "/refactor-arch"
```

### 7.3 Rodar os projetos

```powershell
# Projeto 1
cd code-smells-project
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:SECRET_KEY="sua-chave-forte"
$env:ADMIN_TOKEN="seu-token-admin"
python app.py

# Projeto 2
cd ..\ecommerce-api-legacy
npm install
$env:ADMIN_TOKEN="seu-token-admin"   # opcional
npm start

# Projeto 3
cd ..\task-manager-api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python seed.py
$env:SECRET_KEY="sua-chave-forte"
python app.py
```

> Projetos 1 e 3 usam a porta 5000 por padrão. Rode um por vez ou defina `PORT`.

### 7.4 Validar

```bash
curl http://127.0.0.1:5000/health
curl http://127.0.0.1:5000/produtos
curl http://127.0.0.1:3000/health
curl http://127.0.0.1:3000/api/admin/financial-report
curl http://127.0.0.1:5000/tasks
curl http://127.0.0.1:5000/reports/summary
```

Critérios de aceite:

| Critério | Resultado |
|---|---|
| Fase 1 detecta stack corretamente nos 3 | ✅ 3/3 |
| Fase 2 encontra ≥5 findings nos 3 | ✅ 21/21/21 |
| Fase 2 inclui ≥1 CRITICAL/HIGH nos 3 | ✅ 5/5/4 CRITICAL |
| Fase 3 aplicação funciona nos 3 | ✅ boot + endpoints validados |

---

## 8. Observação sobre git

O repositório já contém os commits da refatoração. No momento desta atualização:

- código refatorado, skill, relatórios e documentação: commitados;
- prints em `Evidencias/`: adicionados ao índice (staged);
- `README.md` e este `doc.md`: atualizados no working tree.

Para o envio final, faltam apenas o commit da documentação/evidências e o push
para o fork público:

```bash
git add README.md doc.md Evidencias
git commit -m "docs: adiciona evidências antes/depois e completa o README"
git push
```

---

## 9. Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills)
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview)
- [The Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills)
- [opencode — config e skills](https://opencode.ai/docs)
