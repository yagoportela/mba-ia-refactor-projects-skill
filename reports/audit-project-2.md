================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript + Node.js + Express 4.18.2
Files:   3 analyzed | ~180 lines of code
Scope:   src/app.js, src/AppManager.js, src/utils.js (package.json/README para stack)
Date:    2026-11-03

## Summary
CRITICAL: 5 | HIGH: 6 | MEDIUM: 5 | LOW: 5
Total: 21 findings

## Findings

### [CRITICAL] Credenciais e chaves hardcoded
File: src/utils.js:1-7
Description: `dbUser`, `dbPass`, `paymentGatewayKey` (`pk_live_****`), `smtpUser` e porta ficam fixos no módulo; a chave de pagamento é usada no checkout.
Impact: qualquer pessoa com acesso ao código compromete banco/pagamento; segredo vazado exige rotação imediata.
Recommendation: mover para `process.env` em `src/config/index.js`, criar `.env.example` e nunca logar a chave.

### [CRITICAL] Weak hash de senha e senha de seed em texto puro
File: src/utils.js:17-23; src/AppManager.js:18
Description: `badCrypto` gera um "hash" concatenando base64 em loop e cortando 10 caracteres; o usuário de seed é inserido com uma senha de 3 dígitos.
Impact: senhas trivialmente reversíveis/colidíveis e credenciais padrão conhecidas.
Recommendation: usar `crypto.scrypt`/bcrypt/argon2 com salt; migrar hashes legados no login; não semear senhas fracas.

### [CRITICAL] Dados de cartão e chave do gateway logados em claro
File: src/AppManager.js:45
Description: `console.log` imprime o número completo do cartão e a `paymentGatewayKey` durante o processamento.
Impact: vazamento de dados de cartão (PCI) e da chave de pagamento em logs.
Recommendation: nunca logar cartão/chave; quando necessário, usar apenas `last4` e logger com redaction.

### [CRITICAL] God Class `AppManager`
File: src/AppManager.js:1-141
Description: a classe inicializa o banco, registra rotas, contém validação, regra de checkout, relatório financeiro, exclusão de usuário e auditoria.
Impact: impossível testar em isolamento; qualquer mudança afeta todo o fluxo.
Recommendation: separar em models, services, controllers, routes, middlewares e composition root.

### [CRITICAL] Bypass de autenticação no checkout para usuário existente
File: src/AppManager.js:40-75
Description: o fluxo busca o usuário por e-mail e, se existir, segue para pagamento/matrícula sem verificar a senha informada (`p`).
Impact: qualquer pessoa pode comprar/matricular usando o e-mail de outra pessoa.
Recommendation: verificar `verifyPassword(pwd, user.pass)` antes de prosseguir; nunca aceitar identidade só pelo e-mail.

### [HIGH] Checkout sem transação atômica
File: src/AppManager.js:50-63
Description: matrícula, pagamento e audit log são inseridos em callbacks aninhados; se uma etapa falhar, as anteriores permanecem gravadas.
Impact: matrícula sem pagamento, pagamento sem log e dados inconsistentes.
Recommendation: `withTransaction` com `BEGIN IMMEDIATE`/`COMMIT`/`ROLLBACK`; validação de curso/pagamento antes da escrita.

### [HIGH] Callback hell e regra de negócio dentro das rotas
File: src/AppManager.js:28-78,80-129
Description: as rotas contêm consultas, pagamento, matrícula, auditoria, relatório e loops assíncronos com 4+ níveis de aninhamento.
Impact: baixa legibilidade, erros escapam e testes são muito difíceis.
Recommendation: rotas finas, controllers, services e Promises/async-await com `asyncHandler`.

### [HIGH] Estado global mutável
File: src/utils.js:9-15
Description: `globalCache` e `totalRevenue` são variáveis de módulo mutáveis; `logAndCache` escreve no cache global e é exportado diretamente.
Impact: vazamento de estado entre requests/testes, condições de corrida e dificuldade de escalar.
Recommendation: injetar um `CacheService` no composition root; remover `totalRevenue` não utilizado.

### [HIGH] Relatório administrativo e exclusão de usuário sem autenticação
File: src/AppManager.js:80-137
Description: `/api/admin/financial-report` expõe faturamento/alunos e `DELETE /api/users/:id` apaga usuários sem qualquer auth/autorização.
Impact: qualquer cliente acessa dados financeiros e destrói contas.
Recommendation: middleware de auth + autorização `admin`; validar token e registrar auditoria.

### [HIGH] Exclusão de usuário deixa matrículas/pagamentos órfãos
File: src/AppManager.js:131-137
Description: apenas `DELETE FROM users` é executado; `enrollments` e `payments` relacionadas permanecem no banco; o erro do `db.run` é ignorado e a resposta é sempre 200.
Impact: dados órfãos, relatórios incorretos e falha silenciosa.
Recommendation: transação com exclusão/cascade das dependências e status HTTP correto; considerar soft delete.

### [HIGH] Dependências desatualizadas com vulnerabilidades conhecidas
File: package.json:9-12
Description: `npm install` reporta 17 vulnerabilidades (2 critical, 8 high, 5 moderate, 2 low) e pacotes transitivos deprecated (`npmlog`, `rimraf`, `glob`, etc.).
Impact: riscos de segurança e manutenção; builds futuros podem quebrar.
Recommendation: atualizar Express/sqlite3 e dependências transitivas, rodar `npm audit fix` com testes e fixar versões compatíveis.

### [MEDIUM] N+1 queries no relatório financeiro
File: src/AppManager.js:89-127
Description: para cada curso busca matrículas; para cada matrícula busca usuário e pagamento; o resultado é montado com callbacks e contadores manuais.
Impact: latência cresce com cursos × matrículas; risco de respostas fora de ordem.
Recommendation: uma query com `JOIN` de courses/enrollments/users/payments e agrupamento em memória.

### [MEDIUM] Validação de input fraca
File: src/AppManager.js:29-35,46
Description: apenas presença de campos é validada; e-mail não é validado; cartão é aceito só por começar com `4`, sem comprimento/Luhn; `c_id` não é convertido/validado.
Impact: dados inválidos, comportamento inesperado e bypass da simulação de pagamento.
Recommendation: validadores centralizados com tipo, formato, ranges e regra de cartão.

### [MEDIUM] Erros ignorados e ausência de tratamento centralizado
File: src/AppManager.js:57-60,133-136; src/utils.js:12-15
Description: o erro do `INSERT` em `audit_logs` é ignorado; o erro do `DELETE` também; não há middleware de erro e cada callback responde manualmente.
Impact: falhas silenciosas, respostas inconsistentes e debugging difícil.
Recommendation: middleware `errorHandler`, `asyncHandler` e lançamento de `AppError` com status.

### [MEDIUM] Banco em memória e seed destrutivo a cada boot
File: src/AppManager.js:7,10-23
Description: o banco é `:memory:` e as tabelas/seed são recriados em todo boot; não há migrations nem persistência.
Impact: dados somem ao reiniciar; impossível validar cenários persistentes; ambiente não representa produção.
Recommendation: configuração de banco via env, migrations e seed idempotente/separado.

### [MEDIUM] Respostas de erro inconsistentes e status inadequados
File: src/AppManager.js:35,38,48,51,55,70,84,135
Description: erros são retornados como texto puro (`"Bad Request"`, `"Erro DB"`) e a exclusão sempre retorna 200, mesmo em falha.
Impact: clientes não conseguem tratar erros de forma programática.
Recommendation: envelope JSON padronizado (`{ error, code }`) e status HTTP corretos.

### [LOW] Magic numbers/strings
File: src/utils.js:19-22; src/AppManager.js:7,12-16,46,57
Description: `10000`, `substring(0, 2)`, `substring(0, 10)`, porta 3000, `'PAID'`/`'DENIED'`, prefixo `"4"` e schema SQL ficam soltos.
Impact: mudanças exigem caça manual; risco de inconsistência.
Recommendation: constantes nomeadas em config/domínio.

### [LOW] Nomenclatura ruim e abreviações
File: src/AppManager.js:29-33,89-127
Description: variáveis `u`, `e`, `p`, `cid`, `cc`, `enr`, `c`, `err` dificultam a leitura do fluxo.
Impact: manutenção lenta e maior chance de erro.
Recommendation: nomes intencionais (`usuarioNome`, `email`, `cursoId`, `cartao`, `matricula`).

### [LOW] Código/dependências não utilizados
File: src/utils.js:2-5,10; src/AppManager.js:2
Description: `dbUser`, `dbPass`, `smtpUser` e `totalRevenue` não são usados; `totalRevenue` é importado em `AppManager.js` sem uso.
Impact: ruído, falsa funcionalidade e confusão sobre o estado da aplicação.
Recommendation: remover exports/imports mortos e rodar `eslint`.

### [LOW] Logging improvisado com `console.log`
File: src/utils.js:13; src/AppManager.js:45,59
Description: logs de negócio, cache, cartão e chave são feitos com `console.log`, sem níveis, timestamp ou redaction.
Impact: operação difícil e vazamento de dados sensíveis.
Recommendation: logger estruturado (`pino`/`winston`) com níveis e redaction.

### [LOW] Ausência de testes e documentação de execução
File: README.md:1-14; package.json:6-8
Description: há apenas script `start`; não há pasta/script de testes, `.env.example` ou documentação de variáveis.
Impact: regressões silenciosas e onboarding lento.
Recommendation: adicionar smoke tests dos endpoints, `.env.example` e README com setup/validação.

## Deprecated API Scan
- Nenhuma API deprecated no código-fonte (não há `new Buffer`, `url.parse`, `res.sendfile` etc.).
- `npm install` reporta pacotes transitivos deprecated (`npmlog`, `rimraf@3`, `glob@7`, `inflight`, entre outros) e 17 vulnerabilidades — ver finding HIGH de dependências.
- Recomendação de upgrade: Express 4.18.2 → 4.21+/5, sqlite3 5.1.6 → versão atual, e revisar `npm audit`.

## Endpoint Inventory (baseline para validação)
| Método | Path | Handler | Arquivo:linha |
|---|---|---|---|
| POST | /api/checkout | checkout | src/AppManager.js:28-78 |
| GET | /api/admin/financial-report | financialReport | src/AppManager.js:80-129 |
| DELETE | /api/users/:id | deleteUser | src/AppManager.js:131-137 |

## Decision Notes
- O banco é em memória; a validação da Fase 3 deve usar o seed do boot.
- O fluxo de pagamento é simulado pelo prefixo do cartão (`4` = aprovado). A refatoração deve preservar esse comportamento de demonstração sem logar o cartão.
- A senha do usuário existente não é verificada no checkout original; corrigir isso é uma mudança de comportamento intencional de segurança.
- O relatório financeiro usa contadores assíncronos; a refatoração deve preservar o formato do array retornado.

================================
Total: 21 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
