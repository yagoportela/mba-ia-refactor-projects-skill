# Template do Relatório de Auditoria — Fase 2

Use **exatamente** esta estrutura. Preencha todos os campos; use `N/A` quando não
se aplicar. Não inclua segredos completos (mascare com `****`). Cada finding deve
ter caminho e linha(s) exatos.

```markdown
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome-do-projeto>
Stack:   <linguagem> + <framework> <versão>
Files:   <N> analyzed | ~<LOC> lines of code
Scope:   <arquivos/pastas incluídos; exclusões>
Date:    <YYYY-MM-DD>

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>
Total: <N> findings

## Findings

### [CRITICAL] <Título específico>
File: <arquivo>:<linha> ou <arquivo>:<início-fim>
Description: <o que foi encontrado, com evidência objetiva>
Impact: <consequência real de negócio/técnica>
Recommendation: <correção acionável, ligada ao playbook>

### [CRITICAL] <Título específico>
File: <arquivo>:<linha>
Description: ...
Impact: ...
Recommendation: ...

### [HIGH] <Título específico>
File: <arquivo>:<linha>
Description: ...
Impact: ...
Recommendation: ...

### [MEDIUM] <Título específico>
File: <arquivo>:<linha>
Description: ...
Impact: ...
Recommendation: ...

### [LOW] <Título específico>
File: <arquivo>:<linha>
Description: ...
Impact: ...
Recommendation: ...

## Deprecated API Scan
- <Status: "Nenhuma API deprecated encontrada" ou lista abaixo>
- [<SEVERIDADE>] <API deprecated> em <arquivo>:<linha> → usar <equivalente moderno>.

## Endpoint Inventory (baseline para validação)
| Método | Path | Handler | Arquivo:linha |
|---|---|---|---|
| GET | /... | ... | ... |

## Decision Notes
- <decisões de escopo, falsos positivos descartados, limitações da análise>

================================
Total: <N> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

## Regras de preenchimento

1. **Summary** deve bater com a contagem real dos findings.
2. **Ordem:** CRITICAL → HIGH → MEDIUM → LOW. Dentro da severidade, maior impacto
   primeiro.
3. **File:** use caminho relativo à raiz do projeto e linhas exatas. Para intervalos,
   use `início-fim`. Múltiplas localizações: separe por vírgula.
4. **Description:** descreva o fato, não opinião. Ex.: "A rota executa
   `cursor.execute(query)` com `query` vindo de `request.get_json()`."
5. **Impact:** explique o risco/efeito. Ex.: "Permite exfiltração e DROP TABLE."
6. **Recommendation:** aponte a transformação concreta do playbook.
7. **Deprecated API Scan:** se não houver, escreva explicitamente. Se houver,
   classifique cada uma (normalmente MEDIUM; HIGH se a API removida quebra build).
8. **Endpoint Inventory:** todos os endpoints descobertos na Fase 1, inclusive
   administrativos, health e auth. Será o baseline da Fase 3.
9. **Decision Notes:** registre falsos positivos, itens fora de escopo (ex.:
   `node_modules`) e limitações (ex.: banco não disponível).
10. **Confirmação:** o relatório termina com a pergunta exata. Não refatore antes
    da resposta.

## Exemplo resumido (para referência de tom)

```markdown
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~780 lines of code
Scope:   app.py, controllers.py, models.py, database.py

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 6 | LOW: 5
Total: 20 findings

## Findings

### [CRITICAL] Hardcoded secret key exposta no /health
File: app.py:7; controllers.py:289
Description: SECRET_KEY fixa em app.py e retornada em claro pelo endpoint /health.
Impact: qualquer cliente obtém a chave de assinatura da aplicação.
Recommendation: mover para variável de ambiente e remover do payload de health.

### [CRITICAL] SQL Injection por concatenação de strings
File: models.py:28,48-49,58-60,68,92,110,127-128
Description: IDs, nomes e filtros de busca são interpolados diretamente em SQL.
Impact: leitura/escrita/exclusão arbitrária no SQLite.
Recommendation: usar placeholders (`?`) e parâmetros em todas as queries.
```

## Observações

- O relatório é a **saída da Fase 2** e deve ser salvo em
  `reports/audit-<slug>.md` (ou `reports/audit-project-N.md` quando o desafio
  definir a numeração).
- Não inclua código corrigido no relatório; ele pertence à Fase 3.
- Não inclua dados reais de usuários nem segredos; mascare.
- Se um finding for muito extenso, cite as linhas principais e resuma o restante
  com "entre outras ocorrências".
