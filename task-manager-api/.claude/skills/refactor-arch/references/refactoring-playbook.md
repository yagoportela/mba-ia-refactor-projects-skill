# Playbook de Refatoração

Receitas concretas para a Fase 3. Cada padrão tem sinais, transformação e
exemplos antes/depois. Adapte a sintaxe à stack; a ideia é agnóstica.

> Antes de aplicar, confirme que o finding correspondente está no relatório e que
> o endpoint afetado está no inventário da Fase 1.

---

## P1. Extrair configuração e segredos para ambiente

**Elimina:** C1 (credenciais hardcoded), parte de H5.
**Sinais:** `SECRET_KEY`, `dbPass`, `paymentGatewayKey`, `smtp_password`, portas e
URLs hardcoded.

**Antes (Python/Flask)**

```python
app.config["SECRET_KEY"] = "minha-chave-****"
app.config["DEBUG"] = True
app.run(host="0.0.0.0", port=5000)
```

**Depois**

```python
# config/settings.py
import os, secrets

class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
    PORT = int(os.environ.get("PORT", "5000"))
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
    ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")
```

```python
# app.py
app.config.from_object(Settings)
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=app.config["PORT"], debug=app.config["DEBUG"])
```

**Depois (Node/Express)**

```js
// src/config/index.js
module.exports = {
  port: Number(process.env.PORT || 3000),
  dbUrl: process.env.DATABASE_URL || ":memory:",
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || "dev-only",
  adminToken: process.env.ADMIN_TOKEN || "",
};
```

Crie `.env.example` com nomes das variáveis e valores fictícios. Nunca versione
`.env`.

**Validação:** a aplicação inicia sem variáveis? Use defaults seguros em dev, mas
falhe explicitamente em produção se `SECRET_KEY`/`ADMIN_TOKEN` estiverem ausentes.

---

## P2. Parametrizar queries (fim da SQL Injection)

**Elimina:** C2.
**Sinais:** `+ str(id)`, `f"...{termo}..."`, template strings em SQL.

**Antes (Python/sqlite3)**

```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute(
    "INSERT INTO produtos (nome, preco) VALUES ('" + nome + "', " + str(preco) + ")"
)
query += " AND nome LIKE '%" + termo + "%'"
```

**Depois**

```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
cursor.execute(
    "INSERT INTO produtos (nome, preco) VALUES (?, ?)",
    (nome, preco),
)
query = "SELECT * FROM produtos WHERE 1=1"
params = []
if termo:
    query += " AND (nome LIKE ? OR descricao LIKE ?)"
    params.extend([f"%{termo}%", f"%{termo}%"])
cursor.execute(query, params)
```

**Antes (Node/sqlite3)**

```js
db.get("SELECT * FROM users WHERE email = '" + email + "'", cb);
```

**Depois**

```js
db.get("SELECT id, name FROM users WHERE email = ?", [email], cb);
```

**Regra:** a estrutura SQL pode ser montada dinamicamente, mas **valores** sempre
vão em bind params.

---

## P3. Quebrar God Class/File em Models + Controllers + Routes

**Elimina:** C3, H1.
**Sinais:** `AppManager.js` com initDb + rotas + negócio; `models.py` com 4
domínios; `controllers.py` com tudo.

**Antes (Node)**

```js
class AppManager {
  initDb() { /* schema + seed */ }
  setupRoutes(app) {
    app.post('/api/checkout', (req, res) => {
      // validação + query + pagamento + matrícula + log
    });
    app.get('/api/admin/financial-report', (req, res) => { /* N+1 */ });
  }
}
```

**Depois**

```js
// src/models/userModel.js
const userModel = {
  findByEmail: (db, email) => dbGet(db, "SELECT id, name FROM users WHERE email = ?", [email]),
  create: (db, data) => dbRun(db, "INSERT INTO users (name, email, pass) VALUES (?, ?, ?)", [data.name, data.email, data.passwordHash]),
};

// src/services/checkoutService.js
class CheckoutService {
  constructor({ db, payment, cache, logger }) { this.db = db; this.payment = payment; this.cache = cache; this.logger = logger; }
  async execute(input) {
    // regra de negócio + transação
  }
}

// src/controllers/checkoutController.js
async function checkout(req, res) {
  const input = validateCheckout(req.body);
  const result = await req.app.locals.checkoutService.execute(input);
  res.status(200).json({ msg: "Sucesso", enrollment_id: result.enrollmentId });
}

// src/app.js (composition root)
const app = express();
app.use(express.json());
app.use('/api', buildRoutes({ checkoutService }));
app.use(errorHandler);
```

**Regra de bolso:** se o arquivo tem mais de um domínio ou mais de uma camada,
separe por domínio primeiro, depois por camada.

---

## P4. Rotas finas + Controller orquestrador

**Elimina:** H1, H3.
**Sinais:** rota com 30+ linhas, validação, cálculo e resposta.

**Antes (Flask)**

```python
@app.route("/produtos", methods=["POST"])
def criar_produto():
    dados = request.get_json()
    if not dados: return jsonify({"erro": "Dados inválidos"}), 400
    if "nome" not in dados: return jsonify({"erro": "Nome é obrigatório"}), 400
    # ... 40 linhas de validação e regra
    id = models.criar_produto(...)
    return jsonify({"dados": {"id": id}}), 201
```

**Depois**

```python
# views/produto_routes.py
@produto_bp.post("/produtos")
def criar_produto():
    return produto_controller.criar(request.get_json())

# controllers/produto_controller.py
def criar(payload):
    data = validate_product_payload(payload)
    product_id = produto_model.create(**data)
    return {"dados": {"id": product_id}, "sucesso": True}, 201
```

**Regra:** rota só conhece HTTP; controller só conhece caso de uso; model só
conhece dados.

---

## P5. Centralizar tratamento de erros

**Elimina:** M4, parte de C6.
**Sinais:** `try/except` repetido, `str(e)` na resposta, `catch` vazio, sem
middleware.

**Antes (Flask)**

```python
try:
    produto = models.get_produto(id)
except Exception as e:
    return jsonify({"erro": str(e)}), 500
```

**Depois**

```python
# middlewares/error_handler.py
class ApiError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status

def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api_error(err):
        return jsonify({"erro": err.message, "sucesso": False}), err.status

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        app.logger.exception("Erro inesperado")
        return jsonify({"erro": "Erro interno", "sucesso": False}), 500

# controller
if not produto:
    raise ApiError("Produto não encontrado", 404)
```

**Antes (Express)**

```js
app.get('/x', (req, res) => {
  db.get(sql, (err, row) => {
    if (err) return res.status(500).send(err.message);
    res.json(row);
  });
});
```

**Depois**

```js
// middlewares/asyncHandler.js
const asyncHandler = (fn) => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);

// middlewares/errorHandler.js
class AppError extends Error {
  constructor(message, status = 400) { super(message); this.status = status; }
}
function errorHandler(err, req, res, next) {
  const status = err.status || 500;
  const message = status >= 500 ? "Erro interno" : err.message;
  res.status(status).json({ error: message });
}

// rota
router.get('/x', asyncHandler(async (req, res) => {
  const row = await model.get(req.params.id);
  if (!row) throw new AppError("Não encontrado", 404);
  res.json(row);
}));
```

---

## P6. Eliminar N+1 com JOIN / IN / eager loading

**Elimina:** M1.
**Sinais:** query dentro de loop; `len(u.tasks)`; buscar itens por pedido.

**Antes (Python/sqlite3)**

```python
for row in pedidos:
    cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
    for item in cursor2.fetchall():
        cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
```

**Depois (uma query + agrupamento)**

```python
cursor.execute("""
    SELECT p.id AS pedido_id, p.usuario_id, p.status, p.total, p.criado_em,
           i.produto_id, i.quantidade, i.preco_unitario, pr.nome AS produto_nome
    FROM pedidos p
    LEFT JOIN itens_pedido i ON i.pedido_id = p.id
    LEFT JOIN produtos pr ON pr.id = i.produto_id
    WHERE p.usuario_id = ?
    ORDER BY p.id
""", (usuario_id,))
```

**Antes (SQLAlchemy)**

```python
for u in User.query.all():
    user_data["task_count"] = len(u.tasks)  # lazy load por usuário
```

**Depois**

```python
rows = (
    db.session.query(User, func.count(Task.id))
    .outerjoin(Task, Task.user_id == User.id)
    .group_by(User.id)
    .all()
)
```

**Antes (Node)**

```js
courses.forEach(c => {
  db.all("SELECT * FROM enrollments WHERE course_id = ?", [c.id], (e, enrs) => {
    enrs.forEach(enr => db.get("SELECT name FROM users WHERE id = ?", [enr.user_id], ...));
  });
});
```

**Depois**

```js
const rows = await dbAll(db, `
  SELECT c.id AS course_id, c.title, u.name AS student, p.amount, p.status
  FROM courses c
  LEFT JOIN enrollments e ON e.course_id = c.id
  LEFT JOIN users u ON u.id = e.user_id
  LEFT JOIN payments p ON p.enrollment_id = e.id
  ORDER BY c.id
`);
// agrupar em memória por course_id
```

---

## P7. Hash forte de senhas + migração de legado

**Elimina:** C5, parte de C6.
**Sinais:** MD5/SHA1, base64, `badCrypto`, senha em texto puro.

**Antes (Python)**

```python
self.password = hashlib.md5(pwd.encode()).hexdigest()
return self.password == hashlib.md5(pwd.encode()).hexdigest()
```

**Depois (Werkzeug, já vem com Flask)**

```python
from werkzeug.security import generate_password_hash, check_password_hash

self.password_hash = generate_password_hash(pwd)

def check_password(self, pwd):
    if self.password_hash.startswith(("scrypt:", "pbkdf2:")):
        return check_password_hash(self.password_hash, pwd)
    # migração transparente de legado
    if self.password_hash == hashlib.md5(pwd.encode()).hexdigest():
        self.password_hash = generate_password_hash(pwd)
        return True
    return False
```

**Antes (Node)**

```js
function badCrypto(pwd) {
  let hash = "";
  for (let i = 0; i < 10000; i++) hash += Buffer.from(pwd).toString('base64').substring(0, 2);
  return hash.substring(0, 10);
}
```

**Depois**

```js
const crypto = require('crypto');
function hashPassword(pwd) {
  const salt = crypto.randomBytes(16).toString('hex');
  const hash = crypto.scryptSync(pwd, salt, 64).toString('hex');
  return `${salt}:${hash}`;
}
function verifyPassword(pwd, stored) {
  const [salt, hash] = stored.split(':');
  const candidate = crypto.scryptSync(pwd, salt, 64).toString('hex');
  return crypto.timingSafeEqual(Buffer.from(hash, 'hex'), Buffer.from(candidate, 'hex'));
}
```

Sempre remova `password`/`password_hash` dos DTOs.

---

## P8. Transações para escritas multi-etapa

**Elimina:** H4.
**Sinais:** checkout/matrícula/pagamento/log; pedido/itens/estoque; exclusão com
dependentes.

**Antes (Python/sqlite3)**

```python
cursor.execute("INSERT INTO pedidos ...")
for item in itens:
    cursor.execute("INSERT INTO itens_pedido ...")
    cursor.execute("UPDATE produtos SET estoque = estoque - ? ...")
db.commit()
```

**Depois**

```python
try:
    cursor.execute("BEGIN IMMEDIATE")
    cursor.execute("INSERT INTO pedidos ...", params)
    pedido_id = cursor.lastrowid
    for item in itens:
        updated = cursor.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?",
            (item["quantidade"], item["produto_id"], item["quantidade"]),
        ).rowcount
        if updated == 0:
            raise ApiError("Estoque insuficiente", 400)
        cursor.execute("INSERT INTO itens_pedido ...", params)
    db.commit()
except Exception:
    db.rollback()
    raise
```

**Antes (Node, callbacks)**

```js
db.run("INSERT INTO enrollments ...", ..., () => {
  db.run("INSERT INTO payments ...", ..., () => {
    db.run("INSERT INTO audit_logs ...", ..., () => res.json(...));
  });
});
```

**Depois (com promise wrapper + transação)**

```js
async function withTransaction(db, fn) {
  await dbRun(db, "BEGIN IMMEDIATE");
  try {
    const result = await fn();
    await dbRun(db, "COMMIT");
    return result;
  } catch (err) {
    await dbRun(db, "ROLLBACK");
    throw err;
  }
}

await withTransaction(db, async () => {
  const enrollmentId = await enrollmentModel.create(db, userId, courseId);
  await paymentModel.create(db, enrollmentId, course.price, status);
  await auditLogModel.create(db, `Checkout curso ${courseId} por ${userId}`);
  return enrollmentId;
});
```

---

## P9. Remover estado global / injetar dependências

**Elimina:** H2, H3.
**Sinais:** `global db_connection`, cache global, `new AppManager()` na rota.

**Antes (Python)**

```python
db_connection = None
def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect("loja.db", check_same_thread=False)
    return db_connection
```

**Depois (conexão por request via `flask.g`)**

```python
from flask import g
import sqlite3

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)
```

**Antes (Node)**

```js
let globalCache = {};
function logAndCache(key, data) { globalCache[key] = data; }
```

**Depois**

```js
class CacheService {
  constructor() { this.store = new Map(); }
  set(key, value) { this.store.set(key, value); }
  get(key) { return this.store.get(key); }
}
// composition root
const cache = new CacheService();
const checkoutService = new CheckoutService({ db, cache, logger });
```

---

## P10. Validação centralizada e allowlist de campos

**Elimina:** M2, parte de H1.
**Sinais:** `request.get_json()` direto; validações duplicadas; mass assignment.

**Antes (Python)**

```python
dados = request.get_json()
nome = dados["nome"]  # KeyError se ausente
preco = dados["preco"]
if preco < 0: ...
```

**Depois**

```python
# utils/validators.py
def validate_product_payload(payload):
    if not isinstance(payload, dict):
        raise ApiError("Dados inválidos", 400)
    nome = payload.get("nome")
    preco = payload.get("preco")
    estoque = payload.get("estoque")
    if not isinstance(nome, str) or not (2 <= len(nome.strip()) <= 200):
        raise ApiError("Nome inválido", 400)
    if not isinstance(preco, (int, float)) or preco < 0:
        raise ApiError("Preço inválido", 400)
    if not isinstance(estoque, int) or estoque < 0:
        raise ApiError("Estoque inválido", 400)
    return {
        "nome": nome.strip(),
        "descricao": str(payload.get("descricao", "")),
        "preco": float(preco),
        "estoque": estoque,
        "categoria": payload.get("categoria", "geral"),
    }
```

**Antes (Node)**

```js
const { usr, eml, pwd, c_id, card } = req.body; // mass assignment implícito
```

**Depois**

```js
function validateCheckout(body) {
  const { name, email, password, courseId, card } = body || {};
  if (!name || !email || !courseId || !card) throw new AppError("Bad Request", 400);
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) throw new AppError("Email inválido", 400);
  if (!/^\d{13,19}$/.test(String(card))) throw new AppError("Cartão inválido", 400);
  return { name: String(name).trim(), email: String(email).toLowerCase(), password, courseId: Number(courseId), card: String(card) };
}
```

---

## P11. Remover dados sensíveis de respostas e logs

**Elimina:** C6.
**Sinais:** `to_dict` com `password`; `/health` com `secret_key`; log de cartão.

**Antes**

```python
return {"id": row["id"], "nome": row["nome"], "email": row["email"], "senha": row["senha"]}
print("Processando cartão " + cc + " na chave " + config.paymentGatewayKey)
```

**Depois**

```python
return {"id": row["id"], "nome": row["nome"], "email": row["email"]}

logger.info("Processando pagamento", extra={
    "card_last4": card[-4:],
    "gateway": "mock",
})
```

```js
// health seguro
res.json({ status: "ok", database: "connected", version: "1.0.0" });
```

**Regra:** DTOs usam allowlist; logs usam redaction; erros internos não vazam.

---

## P12. Substituir APIs deprecated

**Elimina:** M6.
**Sinais:** `datetime.utcnow()`, `Query.get()`, `new Buffer`, `res.sendfile`.

**Antes (Python)**

```python
from datetime import datetime
created_at = datetime.utcnow()
task = Task.query.get(task_id)
```

**Depois**

```python
from datetime import datetime, timezone
created_at = datetime.now(timezone.utc)
task = db.session.get(Task, task_id)
```

**Antes (Node)**

```js
const buf = new Buffer(data);
const parsed = url.parse(req.url);
res.sendfile(path.join(__dirname, 'index.html'));
```

**Depois**

```js
const buf = Buffer.from(data);
const parsed = new URL(req.url, `http://${req.headers.host}`);
res.sendFile(path.join(__dirname, 'index.html'));
```

**Atenção:** Python 3.12 deprecou `datetime.utcnow()`; use timezone-aware. Em
SQLAlchemy 2.x, `Query.get()` é legado; use `session.get`.

---

## P13. Adicionar paginação

**Elimina:** M5.
**Sinais:** `.all()` em listagens, `SELECT *` sem `LIMIT`.

**Antes**

```python
tasks = Task.query.all()
return jsonify([t.to_dict() for t in tasks])
```

**Depois**

```python
page = max(int(request.args.get("page", 1)), 1)
per_page = min(max(int(request.args.get("per_page", 20)), 1), 100)
pagination = Task.query.order_by(Task.id).paginate(page=page, per_page=per_page, error_out=False)
return jsonify({
    "data": [t.to_dict() for t in pagination.items],
    "meta": {"page": page, "per_page": per_page, "total": pagination.total},
})
```

**Node**

```js
const limit = Math.min(Number(req.query.limit || 20), 100);
const offset = Math.max(Number(req.query.offset || 0), 0);
const rows = await dbAll(db, "SELECT ... LIMIT ? OFFSET ?", [limit, offset]);
```

Preserve a compatibilidade: se o cliente antigo não envia paginação, retorne um
default razoável e documente.

---

## P14. Quebrar callback hell com async/await

**Elimina:** H6.
**Sinais:** 4+ níveis de callbacks; erros verificados manualmente.

**Antes**

```js
this.db.get("SELECT ...", [cid], (err, course) => {
  if (err || !course) return res.status(404).send("Curso não encontrado");
  this.db.get("SELECT ...", [e], (err, user) => {
    if (err) return res.status(500).send("Erro DB");
    this.db.run("INSERT ...", [userId, cid], function (err) {
      if (err) return res.status(500).send("Erro Matrícula");
      self.db.run("INSERT ...", [this.lastID], function (err) {
        // ...
      });
    });
  });
});
```

**Depois**

```js
const dbGet = (db, sql, params = []) => new Promise((resolve, reject) =>
  db.get(sql, params, (err, row) => (err ? reject(err) : resolve(row))));
const dbRun = (db, sql, params = []) => new Promise((resolve, reject) =>
  db.run(sql, params, function (err) { err ? reject(err) : resolve(this); }));

async function checkout(input) {
  const course = await courseModel.findActiveById(db, input.courseId);
  if (!course) throw new AppError("Curso não encontrado", 404);
  const user = await userModel.findByEmail(db, input.email);
  const userId = user ? user.id : await userModel.create(db, input);
  return withTransaction(db, async () => {
    const enrollmentId = await enrollmentModel.create(db, userId, course.id);
    await paymentModel.create(db, enrollmentId, course.price, "PAID");
    await auditLogModel.create(db, `Checkout curso ${course.id} por ${userId}`);
    return enrollmentId;
  });
}
```

---

## P15. Restringir/desativar endpoints perigosos

**Elimina:** C4, parte de H5.
**Sinais:** `/admin/query` executando SQL arbitrário; `/admin/reset-db` sem auth.

**Antes**

```python
@app.post("/admin/query")
def executar_query():
    query = request.get_json().get("sql")
    cursor.execute(query)  # backdoor
```

**Depois**

```python
@admin_bp.post("/admin/query")
def executar_query():
    # endpoint desativado por segurança; mantenha a rota respondendo
    raise ApiError("Endpoint removido. Use os relatórios específicos.", 410)

@admin_bp.post("/admin/reset-db")
@require_admin_token
def reset_database():
    ...
```

```python
def require_admin_token(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_app.config["ADMIN_TOKEN"]:
            raise ApiError("Admin desabilitado", 403)
        token = request.headers.get("X-Admin-Token", "")
        if not hmac.compare_digest(token, current_app.config["ADMIN_TOKEN"]):
            raise ApiError("Não autorizado", 401)
        return fn(*args, **kwargs)
    return wrapper
```

Documente a decisão no relatório e no README. Se o endpoint for removido, a
validação deve esperar 410 (não 404) para provar que a rota existe e foi
desativada conscientemente.

---

## Checklist de aplicação do playbook

- [ ] Cada finding CRITICAL/HIGH tem um padrão correspondente aplicado.
- [ ] Queries usam bind params.
- [ ] Segredos saíram do código e dos DTOs.
- [ ] Senhas usam hash forte.
- [ ] Escritas multi-etapa são transacionais.
- [ ] N+1 substituído por JOIN/IN/eager loading.
- [ ] Rotas finas; controllers/serviços coesos.
- [ ] Error handling centralizado.
- [ ] Config centralizado e validado.
- [ ] APIs deprecated substituídas.
- [ ] Endpoints originais preservados e testados.
- [ ] Estrutura final documentada.
