# task-manager-api — Task Manager API (Flask)

API de Task Manager em Python/Flask, evoluída para **MVC** pela skill
`refactor-arch`. O projeto já possuía alguma separação de camadas; a refatoração
moveu a regra das rotas para controllers/services, corrigiu segurança e substituiu
APIs deprecated. Relatório original em `../reports/audit-project-3.md`.

## Stack

- Python 3.12+
- Flask 3.0.0 + Flask-SQLAlchemy 3.1.1
- SQLite (`tasks.db`)

## Estrutura

```text
config/settings.py          # env + defaults seguros
controllers/                # orquestração por domínio
middlewares/                # erros + auth opcional
models/                     # Task/User/Category (hash forte, DTO sem senha)
routes/                     # Blueprints finos (Views/Routes)
services/                   # auth, notificações, relatórios
utils/                      # constantes, erros, validadores, datas
app.py                      # app factory / composition root
seed.py                     # dados de demonstração
```

## Como rodar

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# recria o banco com dados de exemplo (necessário no primeiro boot)
python seed.py

$env:SECRET_KEY="sua-chave-forte"
python app.py
```

A aplicação sobe em `http://127.0.0.1:5000`. Variáveis em `.env.example`.

## Segurança e comportamento

- `SECRET_KEY` vem de env (sem hardcoded).
- Senhas usam `werkzeug.security` (scrypt/PBKDF2), não mais MD5.
- `User.to_dict()` não expõe mais `password`.
- Login retorna um token assinado real (`itsdangerous`), não mais `fake-jwt-token`.
- `AUTH_REQUIRED=true` exige `Authorization: Bearer <token>` em todas as rotas
  exceto `/`, `/health` e `/login`.
- Credenciais SMTP vêm de env; sem configuração, o serviço apenas registra log.
- Relatórios usam agregações (`group_by`/`JOIN`) e listagens usam paginação
  (`page`/`per_page`, máximo 200).
- `datetime.utcnow()` foi substituído por helper com `datetime.now(timezone.utc)`;
  `Query.get()` foi substituído por `db.session.get()`.
- A exclusão de categoria reatribui tasks para `category_id = NULL` em vez de
  deixar órfãos.
- Risco residual: a auth é opt-in (`AUTH_REQUIRED=false` por padrão) para manter
  a compatibilidade dos endpoints originais; habilite em produção.

## Endpoints

| Método | Path |
|---|---|
| GET | `/`, `/health` |
| GET/POST | `/tasks` |
| GET/PUT/DELETE | `/tasks/<id>` |
| GET | `/tasks/search`, `/tasks/stats` |
| GET/POST | `/users` |
| GET/PUT/DELETE | `/users/<id>` |
| GET | `/users/<id>/tasks` |
| POST | `/login` |
| GET | `/reports/summary`, `/reports/user/<id>` |
| GET/POST | `/categories` |
| PUT/DELETE | `/categories/<id>` |

## Validação

O projeto foi validado com 31 requisições cobrindo os 22 endpoints, CRUDs,
relatórios, login, integridade de categoria e o modo `AUTH_REQUIRED`, além de boot
real da aplicação. Veja os logs e o checklist no `README.md` da raiz.
