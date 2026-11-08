# Catálogo de Anti-Patterns e Code Smells

Catálogo usado na Fase 2. Para cada item há **sinais de detecção acionáveis**,
severidade padrão, impacto e recomendação. A severidade pode subir ou descer
conforme o contexto, mas a justificativa deve ser registrada.

> Regra de ouro: um finding sem `arquivo:linha` não entra no relatório.

## Índice de severidades

| Severidade | Uso |
|---|---|
| CRITICAL | Segurança grave, exposição de dados, execução arbitrária, God Class/File, violação total de MVC. |
| HIGH | Violação forte de MVC/SOLID, lógica pesada em rota, estado global, sem transação, sem auth em área sensível. |
| MEDIUM | N+1, duplicação, validação ausente, erro engolido, falta de paginação, API deprecated. |
| LOW | Nomenclatura, magic numbers, código morto, imports não usados, logs improvisados. |

---

## CRITICAL

### C1. Credenciais e segredos hardcoded

**Sinais de detecção**

- `SECRET_KEY = "..."`, `secret_key = "..."`, `app.config["SECRET_KEY"] = "..."`.
- `password = "..."`, `pass = "..."`, `dbPass`, `smtp_password`, `apiKey`,
  `paymentGatewayKey`, `pk_live_...`, `sk_live_...`, tokens JWT.
- Strings de conexão com usuário/senha (`postgres://user:pass@...`).
- Segredo repetido em mais de um arquivo ou retornado em endpoint de health.

**Impacto:** qualquer pessoa com acesso ao código/repositório compromete o
sistema; segredos vazados exigem rotação imediata.

**Recomendação:** mover para variáveis de ambiente (`os.environ`, `process.env`),
criar `.env.example` sem valores reais, validar presença no boot e nunca
serializar segredos em respostas/logs.

---

### C2. SQL/NoSQL Injection por concatenação

**Sinais de detecção**

- `"SELECT ... WHERE id = " + str(id)`, `"WHERE email = '" + email + "'"`.
- `query += " AND nome LIKE '%" + termo + "%'"`.
- `cursor.execute(f"SELECT ... {valor}")`.
- `db.run("... " + req.body.x)`, template strings com input em SQL.
- `$where`, `eval`, `new Function` com input em NoSQL.

**Impacto:** leitura/escrita/exclusão arbitrária de dados, bypass de autenticação,
comprometimento total do banco.

**Recomendação:** queries parametrizadas (`?`, `%s`, `$1`, bind params). Nunca
interpolar input em SQL. Para filtros dinâmicos, monte apenas a estrutura e passe
os valores como parâmetros.

---

### C3. God Class / God File / God Method

**Sinais de detecção**

- Arquivo com >300 linhas e múltiplos domínios (produtos, usuários, pedidos) no
  mesmo módulo.
- Classe que inicializa banco, registra rotas, contém regra de negócio, valida e
  formata resposta.
- Método com >80 linhas ou muitos níveis de aninhamento.
- Nomes genéricos: `AppManager`, `Manager`, `Utils`, `helpers`, `models.py` com
  tudo dentro.

**Impacto:** impossível testar em isolamento; qualquer mudança afeta vários
domínios; alto risco de regressão.

**Recomendação:** separar por domínio e por camada (models, views/routes,
controllers, services, middlewares) conforme `mvc-guidelines.md`.

---

### C4. Execução arbitrária de SQL / endpoint administrativo inseguro

**Sinais de detecção**

- Rota que recebe `{"sql": "..."}` e executa `cursor.execute(query)`.
- `/admin/query`, `/debug/sql`, `/execute`, `/reset-db` sem autenticação.
- `db.exec`, `db.run` com string vinda do body.

**Impacto:** backdoor completo no banco; permite DROP TABLE, exfiltração e
alteração de dados.

**Recomendação:** remover a rota ou desativá-la com 410/403; se precisar de
administração, expor operações específicas, autenticadas e auditadas.

---

### C5. Senhas em texto puro ou weak hash

**Sinais de detecção**

- `password = pwd`, `senha = "****"` em seed/DB.
- `hashlib.md5`, `hashlib.sha1`, `crypto.createHash('md5')`,
  `Buffer.from(pwd).toString('base64')`.
- Função chamada `badCrypto`, `hashPassword` com loop manual.
- Comparação direta `stored == pwd`.

**Impacto:** vazamento de senhas em caso de breach; quebra por rainbow tables.

**Recomendação:** usar `werkzeug.security.generate_password_hash`/
`check_password_hash` (scrypt/PBKDF2), `bcrypt`, `argon2` ou `crypto.scrypt`.
Migrar hashes legados no login, se necessário.

---

### C6. Exposição de dados sensíveis em respostas/logs

**Sinais de detecção**

- `to_dict()` incluindo `password`, `senha`, `secret`, `token`.
- `console.log` de cartão, senha, token ou chave.
- `/health` retornando `secret_key`, `db_path`, `debug`, ambiente interno.
- Mensagens de erro retornando `str(e)` com stack/SQL.

**Impacto:** vazamento de credenciais e dados pessoais; violação de privacidade/
PCI; facilita ataques.

**Recomendação:** remover campos sensíveis dos DTOs; mascarar logs; responder
erros genéricos com correlation id; usar allowlist de campos.

---

## HIGH

### H1. Lógica de negócio pesada em rotas/controllers

**Sinais de detecção**

- Rota com dezenas de validações, cálculos, loops de banco e notificações.
- `app.post(...)`/`@app.route` contendo `if` de regra de negócio, cálculo de
  total, controle de estoque, envio de e-mail.
- Controller importando driver de banco e executando SQL.

**Impacto:** baixa coesão, difícil teste, duplicação e regressão.

**Recomendação:** rota fina (HTTP) → controller (orquestração/validação) →
service (regra de negócio/transação) → model (persistência).

---

### H2. Estado global mutável

**Sinais de detecção**

- `global db_connection`, `let globalCache = {}`, `let totalRevenue = 0`.
- Singleton de conexão compartilhado sem controle de concorrência.
- Cache em memória exportado como módulo.
- Lista global de notificações.

**Impacto:** condições de corrida, vazamento de estado entre testes/usuários,
dificuldade de escalar horizontalmente.

**Recomendação:** injetar dependências; usar conexão por request ou pool; cache
com escopo e TTL; services instanciados no composition root.

---

### H3. Acoplamento forte / ausência de injeção de dependência

**Sinais de detecção**

- `new AppManager()` dentro da rota; `require('../database')` em qualquer lugar.
- Model importando `request`/`response`.
- Controller instanciando driver/DB diretamente.
- Configuração global lida em qualquer módulo.

**Impacto:** testes exigem infraestrutura real; troca de banco/framework afeta
tudo; baixa testabilidade.

**Recomendação:** composition root cria dependências; controllers/services
recebem `db`, `cache`, `logger`, `notifier` por parâmetro/construtor.

---

### H4. Escrita sem transação / integridade parcial

**Sinais de detecção**

- Sequência `INSERT`/`UPDATE` sem `try/commit/rollback` ou transação.
- Checkout cria matrícula, pagamento e log em callbacks separados.
- Criação de pedido insere cabeçalho, itens e baixa estoque sem atomicidade.
- Exclusão de usuário deixa matrículas/pagamentos órfãos.

**Impacto:** dados inconsistentes em falhas parciais; estoque/pagamento divergentes.

**Recomendação:** agrupar escritas relacionadas em transação; validar tudo antes;
usar `db.session.commit/rollback` ou `BEGIN/COMMIT/ROLLBACK`; cascata/soft delete
para dependências.

---

### H5. Ausência de autenticação/autorização em rotas sensíveis

**Sinais de detecção**

- `/admin/*`, `/reports/*`, `DELETE` de usuário sem middleware de auth.
- Login retorna token fake (`"fake-jwt-token-" + id`).
- Rotas confiam em `user_id` do body sem verificar identidade.
- Senha não é verificada no checkout/login.

**Impacto:** acesso indevido a dados, fraude, exclusão de dados.

**Recomendação:** middleware de autenticação (JWT/sessão) + autorização por papel;
validar credenciais; nunca aceitar identidade só do body.

---

### H6. Callback hell / fluxo assíncrono profundamente aninhado

**Sinais de detecção**

- `db.get(..., () => { db.get(..., () => { db.run(..., () => {...}) }) })`.
- 4+ níveis de indentação em arquivo Node.
- Erros verificados manualmente em cada callback.
- Variável `self`/`this` capturada em closures.

**Impacto:** difícil leitura, erros escapam, testes complexos.

**Recomendação:** Promises/async-await, `util.promisify`, serviços pequenos,
`asyncHandler` para capturar erros.

---

## MEDIUM

### M1. Queries N+1

**Sinais de detecção**

- Loop `for` com `SELECT`/`query.get` dentro (produtos, usuários, categorias).
- `len(u.tasks)` dentro de loop (lazy load).
- Para cada pedido, buscar itens; para cada item, buscar produto.
- Para cada curso, buscar matrículas; para cada matrícula, usuário e pagamento.
- `Task.query.filter_by(...).count()` repetido por categoria/usuário.

**Impacto:** latência cresce linearmente com o número de registros; sobrecarga no
banco.

**Recomendação:** JOIN, `IN`, eager loading (`joinedload`/`selectinload`) ou
agregação no banco; buscar em lote e montar em memória.

---

### M2. Validação de input ausente ou incompleta

**Sinais de detecção**

- `request.get_json()` usado direto sem validar tipo/obrigatoriedade.
- `float(preco_min)` sem try/except → 500 com input inválido.
- `data['priority'] < 1` sem validar se é inteiro.
- Checkout aceita cartão só por prefixo, sem comprimento/Luhn.
- Mass assignment (`user.__dict__.update(data)`).

**Impacto:** 500 inesperado, dados inválidos, bypass de regra, insegurança.

**Recomendação:** schema de validação (Pydantic/Marshmallow/Joi/Zod) ou validadores
centralizados; validar tipos, ranges, formatos e campos permitidos.

---

### M3. Duplicação de código/validação/serialização

**Sinais de detecção**

- Mesmo dicionário de produto repetido em 3–4 funções.
- Validação de `create` copiada em `update`.
- `overdue` calculado em vários handlers.
- Listas de status/roles repetidas em arquivos diferentes.

**Impacto:** divergência de comportamento, manutenção custosa.

**Recomendação:** extrair `to_dict()` no model, validadores e constantes
compartilhadas; usar services para regras repetidas.

---

### M4. Tratamento de erros inexistente, genérico ou que vaza detalhes

**Sinais de detecção**

- `except:` ou `except Exception as e:` em todo handler retornando `str(e)`.
- `catch (err) {}` vazio ou `console.log(err)` e segue.
- Sem middleware global de erro (Express/Flask).
- `return jsonify({"erro": str(e)}), 500` expondo SQL/stack.

**Impacto:** erros silenciosos, debugging difícil, vazamento de informação.

**Recomendação:** exceções de domínio (`ApiError`/`AppError`), middleware global,
logs estruturados com contexto, resposta genérica ao cliente.

---

### M5. Falta de paginação / consultas sem limite

**Sinais de detecção**

- `SELECT * FROM ...` sem `LIMIT`.
- `Model.query.all()` em listagens.
- Endpoint que retorna todos os registros sem `page`/`limit`.
- Relatórios que carregam tudo em memória.

**Impacto:** consumo de memória/latência; risco de DoS acidental.

**Recomendação:** `limit/offset`, cursor, `page/per_page` com validação e máximo.

---

### M6. APIs deprecated / obsoletas

**Sinais de detecção**

- Python 3.12+: `datetime.utcnow()` / `datetime.utcfromtimestamp()`.
- SQLAlchemy 2.x: `Query.get()` (legacy) em vez de `db.session.get(Model, id)`.
- Flask: `before_first_request` (removido), `flask.ext.*`, `@app.before_first_request`.
- Node: `new Buffer(...)` (deprecated), `url.parse()` (legacy),
  `crypto.createCipher` (removido), `body-parser` quando `express.json()` basta,
  `res.sendfile()` (usar `res.sendFile()`), `mongoose` callbacks removidos no v7.
- Express 5: `res.send(status)` e assinaturas antigas.
- Dependências com vulnerabilidades conhecidas (`npm audit`, `pip-audit`).

**Impacto:** quebra futura em upgrades, vulnerabilidades, comportamento
inconsistente entre versões.

**Recomendação:** substituir pelo equivalente moderno e registrar a versão-alvo.

#### Tabela de substituições

| Deprecated | Equivalente moderno |
|---|---|
| `datetime.utcnow()` | `datetime.now(timezone.utc)` |
| `datetime.utcfromtimestamp(ts)` | `datetime.fromtimestamp(ts, tz=timezone.utc)` |
| `Model.query.get(id)` (SQLAlchemy 2.x) | `db.session.get(Model, id)` |
| `flask.ext.*` | imports diretos dos pacotes |
| `@app.before_first_request` | inicialização no factory/`with app.app_context()` |
| `new Buffer(data)` (Node) | `Buffer.from(data)` |
| `url.parse(url)` | `new URL(url)` |
| `crypto.createCipher/createDecipher` | `crypto.createCipheriv/createDecipheriv` |
| `res.sendfile(path)` (Express) | `res.sendFile(path)` |
| `body-parser` (Express 4.16+) | `express.json()` / `express.urlencoded()` |
| `mongoose` callbacks (v7+) | Promises/async-await |

---

### M7. CORS permissivo

**Sinais de detecção**

- `CORS(app)` sem `origins`.
- `app.use(cors())` sem `origin`.
- `Access-Control-Allow-Origin: *` em API com autenticação.

**Impacto:** sites maliciosos podem chamar a API com credenciais do usuário.

**Recomendação:** allowlist de origens via env; permitir credenciais apenas para
origens confiáveis.

---

## LOW

### L1. Nomenclatura ruim / abreviações

**Sinais de detecção**

- Variáveis `u`, `e`, `p`, `cid`, `cc`, `enr`, `c`, `t`, `d`, `p1..p5`.
- Funções `doIt`, `handle`, `process`, `manager`.
- `id` como nome de variável em Python (shadow built-in).

**Impacto:** leitura lenta, erros de interpretação.

**Recomendação:** nomes intencionais (`usuario_id`, `cartao`, `matricula`,
`prioridade`), funções com verbo + objeto.

---

### L2. Magic numbers/strings

**Sinais de detecção**

- `10000`, `0.1`, `0.05`, `0.02`, `5000`, `1000` soltos em cálculo.
- Status repetidos `"pending"`, `"PAID"`, `"aprovado"` em vários pontos.
- Portas, limites, tamanhos e cores hardcoded.
- `substring(0, 2)`, `slice(0, 10)`.

**Impacto:** mudanças exigem caça manual; risco de inconsistência.

**Recomendação:** constantes nomeadas em config/constantes de domínio.

---

### L3. Código morto / imports e dependências não usados

**Sinais de detecção**

- Imports não referenciados (`import os`, `json`, `sys`, `time`).
- Funções nunca chamadas (`NotificationService` inteiro, `totalRevenue`).
- Variáveis atribuídas e não lidas.
- Dependências no manifesto sem uso.
- Código comentado por longos trechos.

**Impacto:** ruído, falsa sensação de funcionalidade, builds maiores.

**Recomendação:** remover ou justificar; usar lint (`ruff`, `eslint`) para detectar.

---

### L4. Logs improvisados com `print`/`console.log`

**Sinais de detecção**

- `print("ERRO: ...")`, `console.log` de dados de negócio/segredos.
- Ausência de níveis (info/warn/error), timestamp ou correlação.
- Log de cartão/senha/token.

**Impacto:** difícil operação em produção, vazamento de dados.

**Recomendação:** logger estruturado (`logging`, `pino`, `winston`), níveis,
redaction de campos sensíveis.

---

### L5. Estrutura de resposta inconsistente

**Sinais de detecção**

- Alguns endpoints retornam `{dados}`, outros array direto, outros texto puro.
- Erros ora `{erro}`, ora `{error}`, ora string.
- Status code 200 para erro de validação.

**Impacto:** clientes precisam de lógica especial; difícil documentar/testar.

**Recomendação:** envelope padronizado (`data`, `error`, `meta`) e status HTTP
corretos; documentar no README.

---

### L6. Falta de testes e de documentação de execução

**Sinais de detecção**

- Nenhuma pasta de testes, script `test` ausente ou vazio.
- README sem comando de boot, porta ou variáveis de ambiente.
- Sem `.env.example`.

**Impacto:** regressões silenciosas; onboarding lento.

**Recomendação:** smoke tests de endpoints, testes unitários de services,
README com setup e `.env.example`.

---

## Como pontuar duplicidade

Se o mesmo anti-pattern aparece em vários locais do mesmo arquivo/domínio,
consolide em um finding com múltiplas localizações. Exemplo:

```text
File: models.py:28,48-49,58-60,68,92,110,127-128
```

Se aparece em arquivos/domínios diferentes com causas diferentes, separe.

## Checklist rápido de varredura

- [ ] Segredos/chaves/senhas hardcoded.
- [ ] Concatenação em SQL/NoSQL.
- [ ] Arquivos/classes/métodos gigantes.
- [ ] Rotas administrativas sem auth e execução arbitrária.
- [ ] Senha em texto puro/weak hash e exposição em DTO/log.
- [ ] Regra de negócio em rotas/controllers.
- [ ] Estado global mutável.
- [ ] Escritas sem transação.
- [ ] N+1 e consultas sem limite.
- [ ] Validação ausente e mass assignment.
- [ ] Erros engolidos/vazando.
- [ ] APIs deprecated.
- [ ] CORS permissivo.
- [ ] Magic numbers, nomes ruins, código morto, logs.
