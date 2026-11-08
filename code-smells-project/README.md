# code-smells-project — E-commerce API (Flask)

API de E-commerce em Python/Flask, refatorada para **MVC** pela skill
`refactor-arch`. O relatório da auditoria original está em
`../reports/audit-project-1.md`.

## Stack

- Python 3.12+
- Flask 3.1.1 + Flask-CORS 5.0.1
- SQLite (`loja.db`)

## Estrutura

```text
config/settings.py          # env + defaults seguros
models/                     # persistência e DTOs por domínio
views/                      # Blueprints (rotas finas)
controllers/                # orquestração/validação
middlewares/                # erros e auth admin
services/                   # token e notificações
utils/                      # constantes, erros e validadores
database.py                 # conexão por request, schema e seed
app.py                      # composition root / create_app
```

## Como rodar

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# opcional (recomendado)
$env:SECRET_KEY="sua-chave-forte"
$env:ADMIN_TOKEN="seu-token-admin"

python app.py
```

A aplicação sobe em `http://127.0.0.1:5000`. O SQLite é criado e populado no
primeiro boot. Variáveis disponíveis em `.env.example`.

## Segurança e comportamento

- Queries SQL são parametrizadas (`?`).
- Senhas são armazenadas com `werkzeug.security` (scrypt/PBKDF2); senhas legadas
  em texto puro são migradas no login.
- `/health` não expõe mais `secret_key`, `debug` ou caminho do banco.
- `POST /admin/reset-db` exige `X-Admin-Token` (defina `ADMIN_TOKEN`).
- `POST /admin/query` foi desativado e responde `410 Gone`.
- CORS é restrito por `CORS_ORIGINS` (vazio por padrão fora de debug).
- Login retorna um token assinado (`itsdangerous`), sem expor senha/hash.
- Risco residual: os endpoints de negócio continuam públicos porque o projeto
  original não tinha fluxo de autenticação; as rotas administrativas estão
  protegidas. Para produção, adicione um middleware de auth para clientes.

## Endpoints principais

| Método | Path |
|---|---|
| GET | `/` |
| GET | `/produtos`, `/produtos/busca`, `/produtos/<id>` |
| POST/PUT/DELETE | `/produtos`, `/produtos/<id>` |
| GET | `/usuarios`, `/usuarios/<id>` |
| POST | `/usuarios`, `/login` |
| POST/GET | `/pedidos` |
| GET | `/pedidos/usuario/<usuario_id>` |
| PUT | `/pedidos/<pedido_id>/status` |
| GET | `/relatorios/vendas` |
| GET | `/health` |
| POST | `/admin/reset-db` (token), `/admin/query` (410) |

## Validação

O projeto foi validado com 35 requisições cobrindo todos os endpoints e boot real
da aplicação. Veja os logs e o checklist no `README.md` da raiz.
