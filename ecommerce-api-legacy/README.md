# ecommerce-api-legacy — LMS API (Node.js/Express)

LMS API com fluxo de checkout, refatorada para **MVC** pela skill
`refactor-arch`. O relatório da auditoria original está em
`../reports/audit-project-2.md`.

## Stack

- Node.js 20+
- Express 4.18.2
- SQLite (`sqlite3`), banco em memória por padrão

## Estrutura

```text
src/app.js                  # composition root
src/config/index.js         # env + defaults
src/db/database.js          # schema, seed, wrapper Promise e transações
src/models/                 # acesso a dados
src/services/               # checkout, relatório, usuário, pagamento, cache
src/controllers/            # orquestração HTTP
src/routes/                 # rotas finas
src/middlewares/            # async handler, erro, auth admin
src/utils/                  # erros, logger, senha, validadores
```

## Como rodar

```powershell
npm install
# opcional: protege as rotas admin
$env:ADMIN_TOKEN="seu-token-admin"
npm start
```

A aplicação sobe em `http://127.0.0.1:3000`. O banco default é `:memory:` e o
seed é recriado a cada boot. Use `DATABASE_PATH` para persistir. Variáveis em
`.env.example`.

## Segurança e comportamento

- Segredos/chaves vêm de variáveis de ambiente (nunca hardcoded).
- Senhas usam `crypto.scryptSync` com salt; o seed também é hasheado.
- Cartão nunca é logado; logs usam redaction.
- Checkout valida e-mail, curso e cartão (13–19 dígitos) e exige senha do usuário
  existente.
- Matrícula, pagamento e auditoria são gravados em uma transação.
- Relatório financeiro usa uma única query com `JOIN` (sem N+1).
- Exclusão de usuário remove matrículas/pagamentos relacionados em transação.
- `ADMIN_TOKEN` é opcional em desenvolvimento; quando definido, as rotas admin
  exigem `X-Admin-Token`.
- Risco residual: `npm audit` ainda reporta vulnerabilidades em dependências
  transitivas (2 critical, 8 high no momento da entrega); atualizações profundas
  não foram aplicadas para não quebrar o fluxo neste desafio.

## Endpoints

| Método | Path | Observação |
|---|---|---|
| GET | `/health` | health check |
| POST | `/api/checkout` | fluxo de compra/matrícula |
| GET | `/api/admin/financial-report` | relatório; auth opcional |
| DELETE | `/api/users/:id` | exclusão com cascade; auth opcional |

Exemplos de requisições em `api.http`.

## Validação

O projeto foi validado com 20 checks (checkout, pagamento recusado, auth admin,
cascade, relatório) e boot real da aplicação. Veja os logs e o checklist no
`README.md` da raiz.
