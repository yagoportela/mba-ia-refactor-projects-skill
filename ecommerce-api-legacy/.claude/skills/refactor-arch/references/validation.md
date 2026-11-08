# Validação da Fase 3

Objetivo: provar que a refatoração não quebrou a aplicação e que os problemas
críticos foram eliminados. A validação é obrigatória; "parece funcionar" não é
evidência.

## 1. Preparação

1. Releia o inventário de endpoints da Fase 1.
2. Descubra como instalar dependências e rodar:
   - Python: venv + `pip install -r requirements.txt`; `python app.py`.
   - Node: `npm install`; `npm start`.
3. Verifique portas livres e variáveis de ambiente necessárias.
4. Use um banco/seed limpo quando possível (ou um caminho temporário).
5. Não use dados reais; não faça chamadas externas reais (pagamento/e-mail).

## 2. Checagem estática

Execute o que existir na stack:

| Stack | Comandos |
|---|---|
| Python | `python -m compileall .`, `python -c "import app"`, `ruff check .` (se disponível), `pytest` (se houver) |
| Node | `node --check src/app.js`, `npm test` (se houver), `npx eslint .` (se configurado) |
| Geral | busca por segredos hardcoded, `TODO`, `except:`, `console.log` de dados sensíveis |

Critérios:

- [ ] Nenhum erro de sintaxe/importação.
- [ ] Nenhum segredo real no código (apenas leitura de env).
- [ ] Nenhum `except:` nu novo.
- [ ] Nenhum endpoint administrativo sem proteção.

## 3. Boot

Inicie a aplicação em background e confirme que ela sobe sem traceback:

```powershell
# PowerShell — exemplo
$proc = Start-Process -FilePath ".\.venv\Scripts\python.exe" -ArgumentList "app.py" `
  -WorkingDirectory (Get-Location) -PassThru `
  -RedirectStandardOutput "boot.out.log" -RedirectStandardError "boot.err.log"
Start-Sleep -Seconds 3
Get-Content boot.out.log, boot.err.log
```

Critérios:

- [ ] Processo permanece vivo após 3–5 s.
- [ ] Log de boot mostra a porta correta.
- [ ] Sem traceback/erro de conexão.
- [ ] Banco/schema criado ou migrado.

## 4. Smoke test de endpoints

Teste **todos** os endpoints do inventário. Para cada um, registre:

| Endpoint | Método | Cenário | Status esperado | Status obtido | OK? |
|---|---|---|---|---|---|
| /health | GET | banco ok | 200 | | |
| /produtos | GET | lista | 200 | | |
| /produtos/999999 | GET | inexistente | 404 | | |
| /produtos | POST | payload válido | 201 | | |
| /produtos | POST | payload inválido | 400 | | |
| ... | | | | | |

Regras:

- **Nenhum 5xx inesperado.** 500 só é aceitável se o cenário for comprovadamente
  uma falha interna simulada e estiver documentado.
- 4xx de validação/autenticação são respostas corretas.
- Para endpoints destrutivos, use dados de teste e recrie o seed depois.
- Para endpoints desativados (ex.: SQL arbitrário), espere 410/403, não 200.
- Para rotas protegidas, teste sem token (401/403) e com token (2xx).
- Valide o formato essencial: campos de sucesso, IDs, listas e mensagens.

### Exemplo com Python (sem dependências extras)

```python
import json
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:5000"

def call(method, path, body=None, headers=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        BASE + path,
        data=data,
        method=method,
        headers={"Content-Type": "application/json", **(headers or {})},
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

checks = [
    ("GET", "/health", None, None, 200),
    ("GET", "/produtos", None, None, 200),
    ("GET", "/produtos/1", None, None, 200),
    ("GET", "/produtos/999999", None, None, 404),
]
for method, path, body, headers, expected in checks:
    status, text = call(method, path, body, headers)
    print(f"{method} {path} -> {status} (esperado {expected})")
    assert status == expected, text
```

### Exemplo com Node

```js
const base = "http://127.0.0.1:3000";
const checks = [
  ["GET", "/api/admin/financial-report", 200],
  ["POST", "/api/checkout", 200, { usr: "Teste", eml: "teste@example.com", pwd: "x", c_id: 1, card: "4111222233334444" }],
];
for (const [method, path, expected, body] of checks) {
  const res = await fetch(base + path, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  console.log(method, path, res.status, "esperado", expected);
  if (res.status !== expected) process.exitCode = 1;
}
```

## 5. Re-auditoria

Após a refatoração, faça uma varredura rápida:

- [ ] Nenhum CRITICAL remanescente.
- [ ] Nenhum HIGH remanescente (ou residual documentado).
- [ ] Segredos apenas via env.
- [ ] Queries parametrizadas.
- [ ] Senhas com hash forte e fora dos DTOs.
- [ ] Controllers sem SQL; models sem HTTP.
- [ ] Error handling centralizado.
- [ ] APIs deprecated substituídas.
- [ ] Estrutura MVC criada/evoluída.
- [ ] Endpoints do inventário respondendo.

Atualize o relatório original? Não. Gere uma seção "Residual Risks" no output da
Fase 3 e, se o desafio pedir, um `reports/audit-<slug>-after.md`.

## 6. Critérios de aceite (todos obrigatórios)

- [ ] Fase 1 detectou linguagem/framework corretamente.
- [ ] Fase 2 encontrou ≥5 findings, com ≥1 CRITICAL/HIGH e arquivo:linha.
- [ ] Fase 2 pausou e pediu confirmação.
- [ ] Fase 3 criou/evoluiu a estrutura MVC.
- [ ] Config extraído para módulo e sem hardcoded.
- [ ] Models abstraem dados.
- [ ] Views/Routes separadas.
- [ ] Controllers concentram o fluxo.
- [ ] Error handling centralizado.
- [ ] Entry point claro.
- [ ] Aplicação inicia sem erros.
- [ ] Endpoints originais respondem corretamente.
- [ ] Nenhum commit/push sem pedido explícito.

## 7. Limpeza

- Remova logs temporários, bancos de teste e scripts de smoke test não versionados.
- Não deixe processos rodando em background.
- Não inclua `.env` real; apenas `.env.example`.
- Se criou um banco de teste, remova ou adicione ao `.gitignore`.
