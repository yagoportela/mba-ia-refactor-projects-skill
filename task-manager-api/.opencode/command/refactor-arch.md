---
description: Analisa, audita e refatora este projeto para MVC usando a skill refactor-arch.
agent: build
---

Use the `refactor-arch` skill. Read `.claude/skills/refactor-arch/SKILL.md` and every
file in `.claude/skills/refactor-arch/references/`.

1. Execute Phase 1 (project analysis) and print the summary block.
2. Execute Phase 2 (architecture audit) and save the full report to
   `../reports/audit-project-3.md` (create `../reports/` if it does not exist).
   Then STOP and ask exactly:
   `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]`
   Do not modify any project file before an explicit affirmative answer.
3. Only after explicit confirmation, execute Phase 3 (MVC refactoring) and validate
   boot + every original endpoint. Print the completion block.

Do not run any git command (no init, add, commit, push).
