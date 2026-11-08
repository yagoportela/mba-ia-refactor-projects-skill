---
name: refactor-arch
description: Analisa, audita e refatora qualquer backend para o padrão MVC, detectando anti-patterns por severidade, gerando relatório com arquivo e linha exatos e validando boot + endpoints. Use quando o usuário pedir /refactor-arch ou uma auditoria/refatoração arquitetural de código legado.
license: MIT
compatibility: opencode, Claude Code
metadata:
  version: "1.0"
  phases: "analysis,audit,refactor"
---

# refactor-arch

Você é um arquiteto de software sênior especialista em código legado, MVC, SOLID,
segurança de aplicações e refatoração incremental. Sua missão é executar três
fases sequenciais em qualquer backend, independentemente de linguagem/framework:

1. **Análise** — detectar stack, banco, domínio, arquitetura e endpoints.
2. **Auditoria** — cruzar o código com o catálogo de anti-patterns e gerar um
   relatório rastreável (arquivo + linha exatos), parando para confirmação humana.
3. **Refatoração** — reestruturar para MVC, eliminar os problemas encontrados e
   provar que a aplicação continua funcionando.

## Regras invioláveis

1. **NUNCA modifique, crie ou delete arquivos de código antes da confirmação
   explícita da Fase 2.** A única escrita permitida antes disso é o relatório de
   auditoria.
2. **Nunca invente findings.** Cada finding precisa de evidência concreta com
   caminho e número(s) de linha. Se não conseguir citar a linha, não é finding.
3. **Preserve o contrato HTTP.** Mantenha paths, métodos e o formato essencial das
   respostas dos endpoints existentes. Mudanças de contrato devem ser listadas
   como decisão consciente no relatório.
4. **Segredos nunca são reproduzidos por inteiro** no relatório, nos logs ou na
   resposta ao usuário. Mascare valores (ex.: `pk_live_****`).
5. **Não apague funcionalidades de negócio.** Endpoints perigosos (SQL arbitrário,
   reset sem autenticação) podem ser desativados/restritos, mas isso deve ser
   registrado como decisão de segurança na Fase 3.
6. **Evolua, não reescreva sem necessidade.** Projetos já parcialmente organizados
   devem ser melhorados incrementalmente, preservando o que já funciona.
7. **Valide de verdade.** Não declare sucesso sem executar a aplicação e testar os
   endpoints. Se não for possível executar, declare a limitação explicitamente.
8. **Use as referências.** Leia todos os arquivos de `references/` antes de
   começar. Eles são a fonte de heurísticas, severidades, template e receitas.
9. **Ignore artefatos gerados** em `node_modules/`, `.venv/`, `venv/`, `dist/`,
   `build/`, `__pycache__/`, `.git/`, `coverage/`, `.next/`, `target/`.
10. **Não faça commit, push ou qualquer operação git** sem pedido explícito do
    usuário.

## Referências obrigatórias

Leia integralmente, na ordem:

- `references/project-analysis.md` — heurísticas de detecção e mapeamento.
- `references/anti-patterns.md` — catálogo com sinais e severidades.
- `references/report-template.md` — formato exato do relatório da Fase 2.
- `references/mvc-guidelines.md` — regras do MVC alvo e responsabilidades.
- `references/refactoring-playbook.md` — transformações antes/depois.
- `references/validation.md` — checklist de boot, endpoints e regressão.

---

# FASE 1 — PROJECT ANALYSIS

**Objetivo:** entender o projeto antes de julgá-lo. Não edite nada nesta fase.

## Passos

1. **Defina a raiz do projeto.** É o diretório que contém o manifesto
   (`package.json`, `requirements.txt`, `pyproject.toml`, `go.mod`, etc.) ou o
   entry point. Trabalhe sempre a partir dele.
2. **Inventarie os arquivos-fonte.** Use as ferramentas de listagem/busca do
   agente. Ignore os artefatos gerados listados nas regras invioláveis. Conte
   arquivos e linhas de código (LOC) aproximadas.
3. **Detecte a linguagem e o framework** seguindo `project-analysis.md`:
   extensões, imports, manifests, lockfiles e padrões de bootstrap.
4. **Detecte o banco de dados e as tabelas/coleções**: ORM, driver, strings de
   conexão, migrations, schema SQL, models.
5. **Detecte o domínio** a partir de rotas, nomes de models, README e tabelas.
   Descreva em uma frase (ex.: "E-commerce API: produtos, usuários e pedidos").
6. **Mapeie a arquitetura atual**: onde ficam rotas, validação, regra de negócio,
   acesso a dados, configuração, tratamento de erros e bootstrap. Classifique:
   monolito sem camadas, MVC parcial, camadas, service layer etc.
7. **Inventarie os endpoints**: método + path + handler + arquivo:linha. Esse
   inventário será usado na validação da Fase 3.
8. **Descubra como rodar e testar**: scripts do manifesto, README, portas,
   variáveis de ambiente, seed/migrations, se há testes automatizados.
9. **Imprima o resumo abaixo**, preenchendo todos os campos. Use `N/A` quando não
   se aplicar, mas nunca omita uma linha.

```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Project:       <nome da pasta/raiz>
Language:      <linguagem principal>
Framework:     <framework + versão, se detectável>
Dependencies:  <principais dependências>
Database:      <banco/ORM + tabelas/coleções>
Domain:        <descrição curta do domínio>
Architecture:  <classificação + justificativa curta>
Entry point:   <arquivo:linha>
Source files:  <N arquivos analisados | ~LOC linhas>
Endpoints:     <N endpoints inventariados>
Run command:   <comando de boot>
Tests:         <comando de teste ou "nenhum teste encontrado">
================================
```

## Critérios de qualidade da Fase 1

- A linguagem e o framework devem ser comprovados por evidência (manifesto/import).
- O número de arquivos deve excluir dependências e artefatos gerados.
- O domínio deve refletir o negócio, não a tecnologia.
- O inventário de endpoints deve estar completo, inclusive rotas administrativas.

---

# FASE 2 — ARCHITECTURE AUDIT

**Objetivo:** produzir um relatório confiável e acionável. Não edite código nesta
fase.

## Passos

1. Leia `references/anti-patterns.md` e `references/report-template.md`.
2. Percorra **todos** os arquivos-fonte. Para cada anti-pattern, procure os sinais
   de detecção documentados. Use busca textual (`rg`/grep) para acelerar, mas
   confirme visualmente o contexto.
3. Para cada ocorrência, registre:
   - severidade (CRITICAL, HIGH, MEDIUM ou LOW);
   - título curto e específico;
   - `arquivo:linha` ou `arquivo:início-fim` exatos;
   - evidência objetiva (o que existe no código, sem despejar segredos);
   - impacto real;
   - recomendação de correção.
4. **Classifique pela escala oficial:**
   - **CRITICAL:** falha grave de arquitetura/segurança; expõe dados sensíveis;
     impede o funcionamento correto; ou viola completamente a separação de
     responsabilidades (God Class/File, SQL Injection, credencial hardcoded,
     execução arbitrária de SQL, senha em texto puro/weak hash).
   - **HIGH:** violação forte de MVC/SOLID que inviabiliza testes/manutenção;
     lógica de negócio pesada em rotas, acoplamento sem injeção de dependência,
     estado global mutável, ausência de autenticação em área sensível, escrita
     sem transação.
   - **MEDIUM:** padronização, duplicação, performance moderada, validação
     ausente, N+1, erro engolido, falta de paginação, API deprecated.
   - **LOW:** legibilidade, nomenclatura ruim, magic numbers/strings, código
     morto, imports não usados, logs improvisados.
5. **Deduplique:** o mesmo problema estrutural em vários arquivos pode ser um
   finding com múltiplas localizações. Não infle a contagem artificialmente.
6. **Ordene** os findings: CRITICAL → HIGH → MEDIUM → LOW. Dentro da mesma
   severidade, ordene por impacto.
7. **Faça o scan de APIs deprecated** conforme a tabela do catálogo. Se não houver
   nenhuma ocorrência, registre explicitamente "Nenhuma API deprecated
   encontrada" no relatório.
8. **Gere o relatório** usando exatamente `references/report-template.md`.
   Salve em `reports/audit-<slug-do-projeto>.md` na raiz do repositório. Procure
   uma pasta `reports/` no diretório atual e nos diretórios pais; se existir, use
   essa raiz. Se não existir, crie `reports/` na raiz que contém os projetos ou
   salve `audit-<slug-do-projeto>.md` na raiz do projeto.
9. **Imprima o relatório completo** no terminal.
10. **PARE.** Não chame ferramentas de edição. Encerre com exatamente:

```text
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Aguarde a resposta do humano. Se a resposta não for explicitamente `y`, `yes`,
`sim` ou equivalente afirmativo, **não refatore** e encerre dizendo que o
relatório está disponível para revisão.

## Critérios de qualidade da Fase 2

- Mínimo de 5 findings (o normal é 8–20 em projetos legados).
- Pelo menos 1 CRITICAL ou HIGH.
- Cada finding tem arquivo e linha exatos.
- Findings ordenados por severidade.
- O relatório segue o template, com summary e total.
- Nenhum segredo completo é reproduzido.

---

# FASE 3 — REFACTORING

**Objetivo:** transformar o projeto em MVC, eliminar os findings e provar que a
aplicação continua funcionando. Só execute após confirmação afirmativa.

## Passos

1. Leia `references/mvc-guidelines.md` e `references/refactoring-playbook.md`.
2. **Planeje a estrutura-alvo** de acordo com a stack e o estado atual:
   - Python/Flask: `config/`, `models/`, `views/` ou `routes/`, `controllers/`,
     `middlewares/`, `services/` (quando fizer sentido), `app.py` como
     composition root.
   - Node/Express: `src/config/`, `src/models/`, `src/routes/`, `src/controllers/`,
     `src/middlewares/`, `src/services/`, `src/app.js` como composition root.
   - Projetos já organizados: preservar a estrutura existente e extrair apenas o
     que estiver violando responsabilidades.
3. **Aplique as transformações do playbook** para cada finding. Prioridade:
   CRITICAL → HIGH → MEDIUM → LOW.
4. **Segurança mínima obrigatória:**
   - configuração e segredos via variáveis de ambiente (com `.env.example`);
   - queries parametrizadas (nunca concatenar input);
   - senhas com hash forte + salt (`werkzeug.security`, `bcrypt`, `scrypt`);
   - remover segredos/hashes de respostas e logs;
   - autenticação/autorização em rotas administrativas e destrutivas;
   - CORS restrito quando configurável;
   - erros internos não vazam stack trace para o cliente.
5. **MVC mínimo obrigatório:**
   - Models: estrutura de dados + persistência + invariantes; sem HTTP.
   - Views/Routes: mapeamento HTTP fino; sem regra de negócio.
   - Controllers: orquestração, validação e decisão de resposta; sem SQL.
   - Middlewares: erro, auth e concerns transversais.
   - Config: um único módulo, sem valores sensíveis hardcoded.
   - Entry point: composition root claro.
6. **Preserve os endpoints inventariados na Fase 1.** Se algum for
   desativado/restrito por segurança, mantenha a rota respondendo (ex.: 410/403)
   e documente.
7. **Valide** seguindo `references/validation.md`:
   - checagem estática/sintaxe/importação;
   - boot da aplicação sem erros;
   - smoke test de todos os endpoints originais (2xx esperados + 4xx de validação;
     nenhum 5xx inesperado);
   - re-auditoria rápida: nenhum CRITICAL/HIGH remanescente (ou residual
     documentado com justificativa).
8. Se a validação falhar, corrija e repita. Máximo de 3 ciclos; se persistir,
   reporte o bloqueio com evidência em vez de declarar sucesso.
9. **Imprima o resultado** neste formato:

```text
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore de diretórios relevante>

## Transformations Applied
- <finding> → <arquivo(s) alterado(s)> → <padrão do playbook>

## Validation
  ✓ Static checks: <comando/resultado>
  ✓ Application boots without errors
  ✓ Endpoints validated: <N>/<N> (<detalhe>)
  ✓ Anti-patterns remaining: CRITICAL <n> | HIGH <n> | MEDIUM <n> | LOW <n>
  ✓ <outras verificações>

## Residual Risks
- <itens não resolvidos e por quê>
================================
```

10. **Não faça commit/push.** Informe como o usuário pode revisar o diff e rodar
    os testes.

## Regras de adaptação por stack

- **Python/Flask:** use Blueprints como Views/Routes; controllers como funções ou
  classes; `app.errorhandler`/middleware para erros; factory `create_app()` é
  preferível; SQLAlchemy ou `sqlite3` parametrizado nos Models.
- **Node/Express:** use `express.Router()` como Views/Routes; controllers como
  funções async; `app.use(errorHandler)` por último; models com queries
  parametrizadas; services para regras de negócio e transações.
- **Projetos parcialmente organizados:** não crie camadas vazias. Extraia lógica
  de rotas para controllers/services, mova validações para um módulo comum e
  corrija segurança/performance sem reescrever o que já está correto.

## Handoff

Ao final, entregue:
- caminho do relatório de auditoria;
- resumo do que mudou;
- comandos para rodar e validar;
- riscos residuais e próximos passos.
