# Guidelines de Arquitetura MVC

Objetivo: definir o alvo da Fase 3 para APIs backend, com responsabilidades claras
e direção de dependência saudável. MVC aqui significa **Model–View–Controller**
aplicado a APIs: a "View" é a camada de rotas/HTTP.

## 1. Visão geral

```text
Cliente HTTP
    │
    ▼
View / Routes  ──►  Controller  ──►  Service (opcional)  ──►  Model  ──►  Banco
    │                   │                    │                  │
    │                   │                    │                  └─ persistência, invariantes, serialização
    │                   │                    └─ regras de negócio, transações, integrações
    │                   └─ validação, autorização, orquestração, decisão de resposta
    └─ mapeamento URL/método, parsing mínimo, status HTTP
```

**Direção de dependência:** Views → Controllers → Services → Models. Nunca o
contrário. Models não importam HTTP. Routes não importam banco.

## 2. Model

**Responsabilidades**

- Representar a entidade/tabela/coleção e seus relacionamentos.
- Encapsular persistência (queries parametrizadas, ORM) e mapeamento de dados.
- Aplicar invariantes de domínio que não dependem de HTTP (ex.: status válido,
  cálculo de total, verificação de estoque).
- Serializar para DTO seguro (`to_dict`), **sem campos sensíveis**.
- Expor operações de dados coesas (`find_by_id`, `list`, `create`, `update`).

**Não pode**

- Ler `request`, `response`, headers, status HTTP.
- Retornar HTML/JSON diretamente com status code.
- Conter validação de formato de request (isso é do controller/schema).
- Enviar e-mail, acessar cache ou chamar serviços externos.

**Exemplo (Python/SQLAlchemy)**

```python
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {"id": self.id, "email": self.email}  # nunca password_hash
```

**Exemplo (Node/sqlite3)**

```js
const userModel = {
  findById(db, id) {
    return dbGet(db, "SELECT id, name, email FROM users WHERE id = ?", [id]);
  },
};
```

## 3. View / Routes

**Responsabilidades**

- Declarar o mapa HTTP: método, path, parâmetros de rota.
- Aplicar middlewares da rota (auth, validação de schema, rate limit).
- Delegar para o controller, repassando dados já parseados.
- Retornar a resposta produzida pelo controller (ou deixar o controller
  retornar). Em Express, `res` pode ser passado ao controller.
- Manter-se fina: idealmente 1–8 linhas por handler.

**Não pode**

- Executar SQL/ORM.
- Conter regra de negócio (cálculo de preço, estoque, permissão complexa).
- Validar regras de domínio profundas.
- Capturar `Exception` genérica em cada handler (usar middleware global).

**Flask**

```python
# views/task_routes.py
task_bp = Blueprint("tasks", __name__)

@task_bp.get("/tasks")
def list_tasks():
    return task_controller.list_tasks(request.args)
```

**Express**

```js
// routes/taskRoutes.js
const router = express.Router();
router.get("/tasks", asyncHandler(taskController.listTasks));
module.exports = router;
```

## 4. Controller

**Responsabilidades**

- Orquestrar o caso de uso: parsear/validar input, autorizar, chamar
  services/models, decidir status e corpo da resposta.
- Conter validações de entrada (formato, obrigatoriedade, ranges) ou delegá-las
  a schemas.
- Converter erros de domínio em respostas HTTP.
- Manter-se coeso por domínio (produto, pedido, usuário etc.).

**Não pode**

- Executar SQL/ORM diretamente.
- Conter cálculos de negócio extensos (isso é service).
- Conhecer detalhes de framework de banco.
- Duplicar validações em vários handlers (extrair schema/validator).

**Exemplo (Flask)**

```python
def create_product(payload):
    data = validate_product_payload(payload)
    product_id = product_model.create(**data)
    return {"data": {"id": product_id}, "success": True}, 201
```

**Exemplo (Express)**

```js
async function checkout(req, res) {
  const input = validateCheckout(req.body);
  const result = await checkoutService.execute(input);
  res.status(200).json({ msg: "Sucesso", enrollment_id: result.enrollmentId });
}
```

## 5. Service (opcional, recomendado)

Use quando a regra:

- envolve mais de um model;
- precisa de transação;
- chama integração externa (pagamento, e-mail, cache);
- é reutilizada por mais de um controller.

**Responsabilidades:** regra de negócio, transações, orquestração de integrações,
lançamento de erros de domínio.

**Não pode:** conhecer `req`/`res`, status HTTP ou detalhes de roteamento.

## 6. Middleware

**Responsabilidades**

- Tratamento centralizado de erros (converter exceção → resposta padronizada).
- Autenticação/autorização.
- Correlação/logging, CORS, rate limit.
- Validação de schema na borda, se adotado.

**Ordem no Express:** rotas → 404 handler → error handler (último). No Flask:
registrar `errorhandler` no app factory.

```js
// middlewares/errorHandler.js
module.exports = (err, req, res, next) => {
  const status = err.status || 500;
  const message = status >= 500 ? "Erro interno" : err.message;
  res.status(status).json({ error: message });
};
```

## 7. Config

**Responsabilidades**

- Centralizar configuração e leitura de variáveis de ambiente.
- Fornecer defaults seguros para desenvolvimento.
- Validar variáveis obrigatórias no boot.

**Não pode**

- Conter segredos reais versionados.
- Ser importado por models para decidir regra de negócio.
- Espalhar `os.environ`/`process.env` por todo o código.

```python
# config/settings.py
import os, secrets

class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
    ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")
```

```js
// src/config/index.js
module.exports = {
  port: Number(process.env.PORT || 3000),
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || "dev-only",
  databaseUrl: process.env.DATABASE_URL || ":memory:",
};
```

## 8. Composition root / entry point

- Único lugar que monta dependências e registra rotas/middlewares.
- Flask: `create_app()` retorna app configurado; `app.py` chama e roda.
- Express: `src/app.js` cria app, registra middlewares/rotas e exporta; `server.js`
  ou bloco `listen` inicia.
- Evita imports circulares e estado global.

```python
def create_app(settings=None):
    app = Flask(__name__)
    app.config.from_object(settings or Settings)
    db.init_app(app)
    register_blueprints(app)
    register_error_handlers(app)
    return app
```

## 9. Estrutura-alvo por stack

### Python/Flask (monolito legado)

```text
config/settings.py
database.py                  # conexão/schema
models/
  produto.py
  usuario.py
  pedido.py
views/                       # ou routes/
  produto_routes.py
  usuario_routes.py
  pedido_routes.py
  relatorio_routes.py
controllers/
  produto_controller.py
  usuario_controller.py
  pedido_controller.py
  relatorio_controller.py
middlewares/error_handler.py
services/                    # opcional
app.py                       # composition root
```

### Python/Flask (já parcialmente organizado)

Preserve `models/`, `routes/`, `services/`, `utils/`; adicione `controllers/`,
`config/`, `middlewares/`; mova lógica de rota para controllers e validações para
`utils/validators.py`; mantenha os nomes existentes quando fizer sentido.

### Node/Express

```text
src/
  config/index.js
  db/database.js
  models/
    userModel.js
    courseModel.js
    enrollmentModel.js
    paymentModel.js
    auditLogModel.js
  services/
    checkoutService.js
    paymentService.js
  controllers/
    checkoutController.js
    reportController.js
    userController.js
  routes/
    index.js
    checkoutRoutes.js
    reportRoutes.js
    userRoutes.js
  middlewares/
    errorHandler.js
    asyncHandler.js
  utils/
    password.js
    logger.js
  app.js                     # composition root
  server.js                  # listen (opcional)
```

## 10. Regras de ouro

1. Uma rota = uma responsabilidade HTTP; um controller = um domínio.
2. Model não conhece HTTP; View/Route não conhece SQL; Controller não conhece
   driver de banco.
3. Toda escrita multi-etapa é transacional.
4. Toda query recebe input por parâmetro.
5. Todo DTO tem allowlist de campos; nunca `SELECT *` + `**row` para resposta.
6. Erros de domínio são explícitos; erros internos não vazam.
7. Configuração e segredos vêm do ambiente.
8. A aplicação deve poder ser importada/criada sem efeitos colaterais destrutivos.
9. Preserve contratos HTTP; mudanças conscientes são documentadas.
10. A estrutura deve ser copiável: nenhum caminho absoluto, nenhum nome de
    projeto hardcoded.

## 11. Checklist de aderência ao MVC

- [ ] Existe um composition root claro.
- [ ] Models abstraem dados e não importam HTTP.
- [ ] Views/Routes só mapeiam HTTP e delegam.
- [ ] Controllers orquestram e validam; não têm SQL.
- [ ] Services concentram regra de negócio/transação quando necessário.
- [ ] Config centralizado; zero segredo hardcoded.
- [ ] Error handling centralizado.
- [ ] Cada domínio tem arquivos coesos (sem God File).
- [ ] Dependências apontam para dentro (HTTP → domínio → dados).
- [ ] Endpoints originais preservados.
