# Análise de Projeto — Heurísticas de Detecção

Este arquivo ensina a Fase 1 a identificar linguagem, framework, banco, domínio,
arquitetura e endpoints **sem assumir a stack**. Sempre cite evidências.

## 1. Detecção de linguagem

| Evidência | Linguagem provável |
|---|---|
| `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, arquivos `.js/.mjs/.cjs/.ts` | JavaScript/TypeScript |
| `requirements.txt`, `pyproject.toml`, `Pipfile`, `poetry.lock`, arquivos `.py` | Python |
| `go.mod`, `go.sum`, arquivos `.go` | Go |
| `pom.xml`, `build.gradle`, arquivos `.java` | Java |
| `Gemfile`, `Gemfile.lock`, arquivos `.rb` | Ruby |
| `composer.json`, arquivos `.php` | PHP |
| `Cargo.toml`, arquivos `.rs` | Rust |
| `*.csproj`, `*.sln`, arquivos `.cs` | C#/.NET |

Refine com imports e bootstrap:

- Python: `from flask import Flask`, `from fastapi import FastAPI`, `import django`.
- Node: `require('express')`, `import express from 'express'`, `require('fastify')`.
- TypeScript: `tsconfig.json`, anotações de tipo, `import type`.
- Se houver múltiplas linguagens, escolha a que contém o entry point do backend e
  registre as demais como "linguagens auxiliares".

## 2. Detecção de framework

| Sinal | Framework |
|---|---|
| `Flask(__name__)`, `flask`, `@app.route`, `Blueprint`, `flask_sqlalchemy` | Flask |
| `FastAPI()`, `@app.get`, `uvicorn`, `pydantic` | FastAPI |
| `django-admin`, `urlpatterns`, `settings.py`, `models.Model` | Django |
| `express()`, `app.use(express.json())`, `app.listen`, `express.Router()` | Express |
| `NestFactory.create`, `@Controller`, `@Module` | NestJS |
| `fastify()`, `fastify.register` | Fastify |
| `new Koa()`, `koa-router` | Koa |

Versões: leia `package.json`/lockfile ou `requirements.txt`. Se não for possível,
registre "não determinada" em vez de inventar.

## 3. Detecção de banco de dados

Procure por drivers, ORMs, strings de conexão, migrations e schema:

- **SQLite:** `sqlite3`, `sqlite:///`, arquivos `*.db`, `*.sqlite`, `:memory:`.
- **PostgreSQL:** `psycopg2`, `asyncpg`, `pg`, `postgres://`, `DATABASE_URL`.
- **MySQL/MariaDB:** `pymysql`, `mysql2`, `mysql://`.
- **MongoDB:** `pymongo`, `mongoose`, `MONGO_URI`, `mongoose.connect`.
- **Redis:** `redis`, `ioredis`, uso de cache/sessão.
- ORMs: SQLAlchemy (`db.Model`, `session.query`), Prisma (`schema.prisma`),
  Sequelize (`sequelize.define`), TypeORM (`@Entity`), Mongoose (`Schema`).
- Tabelas/coleções: leia `CREATE TABLE`, models, migrations, `db.create_all()`,
  seeds. Liste os nomes reais, não os inferidos.

Se o banco for em memória, registre isso (impacta persistência e validação).

## 4. Detecção de domínio

Combine três fontes:

1. **Rotas:** substantivos e verbos dos paths (`/produtos`, `/checkout`,
   `/tasks`, `/reports`).
2. **Models/tabelas:** entidades e relacionamentos.
3. **README/docs:** descrição do negócio.

Escreva uma frase curta orientada a negócio. Exemplos:

- "E-commerce API: catálogo de produtos, usuários, pedidos e relatório de vendas."
- "LMS API: cursos, matrículas, pagamentos e checkout."
- "Task Manager API: tarefas, usuários, categorias e relatórios de produtividade."

Evite descrever apenas a tecnologia ("API Flask com SQLite").

## 5. Mapeamento de arquitetura

Percorra o fluxo de uma requisição e responda:

| Pergunta | Onde olhar |
|---|---|
| Onde as rotas são declaradas? | `app.py`, `app.js`, `routes/`, `controllers/` |
| Onde a validação de input acontece? | rotas, controllers, schemas, helpers |
| Onde a regra de negócio vive? | rotas, controllers, services, models |
| Onde o banco é acessado? | models, services, rotas (anti-pattern) |
| Onde a configuração/segredos vivem? | arquivo de config, `.env`, hardcoded |
| Onde os erros são tratados? | try/except por handler, middleware global |
| Qual é o entry point? | `app.py`, `src/app.js`, `main.ts`, `manage.py` |
| Como as dependências são ligadas? | imports diretos, factory, DI container |

Classificações úteis:

- **Monolito sem camadas:** rotas, SQL, validação e negócio no mesmo arquivo.
- **MVC parcial:** existem pastas `models/` e `routes/`, mas controllers/services
  estão vazios ou as rotas concentram regra de negócio.
- **Camadas:** models, services, controllers e rotas separados; verificar se as
  dependências apontam na direção correta.
- **Service layer:** regras em services; rotas finas; models de persistência.
- **God Class/File:** um arquivo/classe concentra múltiplos domínios e camadas.

### Sinais de acoplamento e direção de dependência

- Model importando `request`/`response` → violação (Model não deve conhecer HTTP).
- Route contendo SQL/ORM → violação (View/Route não deve acessar dados).
- Controller contendo `SELECT`/`INSERT` → violação (Controller não deve ter SQL).
- Config importada por models sem injeção → acoplamento aceitável para settings,
  mas não para segredos hardcoded.
- Estado global mutável (`global`, `let cache = {}`, singleton de conexão) →
  risco de concorrência e testes.

## 6. Inventário de endpoints

Busque por:

- Flask: `@app.route`, `@bp.route`, `add_url_rule`, `Blueprint`.
- FastAPI: `@app.get/post/...`, `APIRouter`.
- Express: `app.get/post/put/delete/patch`, `router.get/...`.
- NestJS: `@Get`, `@Post`, `@Controller`.
- Django: `path()`, `url()`, `urlpatterns`.

Registre método, path, handler e `arquivo:linha`. Inclua rotas administrativas,
health checks, autenticação e endpoints destrutivos. Eles serão testados na Fase 3.

## 7. Contagem de arquivos e LOC

Conte apenas fonte, excluindo dependências e artefatos:

```powershell
# PowerShell (Windows)
Get-ChildItem -Recurse -File -Include *.py,*.js,*.ts,*.jsx,*.tsx |
  Where-Object { $_.FullName -notmatch '\\(node_modules|\.venv|venv|dist|build|__pycache__|\.git)\\' } |
  ForEach-Object { (Get-Content $_.FullName).Count } |
  Measure-Object -Sum -Count
```

```bash
# Bash (Unix/macOS)
find . -type f \( -name '*.py' -o -name '*.js' -o -name '*.ts' \) \
  -not -path '*/node_modules/*' -not -path '*/.venv/*' -not -path '*/dist/*' \
  -not -path '*/build/*' -not -path '*/__pycache__/*' \
  -print0 | xargs -0 wc -l
```

Arredonde LOC para cima (ex.: "~800 linhas"). O relatório deve dizer quantos
arquivos foram analisados; use o mesmo critério do inventário.

## 8. Descoberta de comandos de execução e teste

| Stack | Boot provável | Teste provável |
|---|---|---|
| Python/Flask | `python app.py` ou `flask run` | `pytest`, `unittest` |
| Python/FastAPI | `uvicorn main:app --reload` | `pytest` |
| Node/Express | `npm start`, `node src/app.js` | `npm test`, `jest`, `vitest` |
| NestJS | `npm run start:dev` | `npm test` |
| Django | `python manage.py runserver` | `python manage.py test` |

Verifique portas e variáveis de ambiente no código/README. Se não houver testes,
registre "nenhum teste encontrado" e planeje um smoke test na Fase 3.

## 9. Template de saída da Fase 1

```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Project:       code-smells-project
Language:      Python
Framework:     Flask 3.1.1
Dependencies:  flask-cors 5.0.1
Database:      SQLite (loja.db) — produtos, usuarios, pedidos, itens_pedido
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — 4 arquivos, sem separação de camadas
Entry point:   app.py:80
Source files:  4 arquivos | ~780 linhas
Endpoints:     19 endpoints inventariados
Run command:   python app.py
Tests:         nenhum teste encontrado
================================
```

## 10. Checklist da Fase 1

- [ ] Linguagem comprovada por manifesto/import.
- [ ] Framework e versão (ou "não determinada") registrados.
- [ ] Banco/ORM e tabelas reais listados.
- [ ] Domínio descrito em linguagem de negócio.
- [ ] Arquitetura classificada com justificativa.
- [ ] Entry point e comando de boot identificados.
- [ ] Endpoints inventariados com arquivo:linha.
- [ ] Arquivos gerados/dependências excluídos da contagem.
- [ ] Resumo impresso no formato padronizado.
