---
description: Analisa, audita e refatora este projeto para MVC usando a skill refactor-arch.
---

Use the `refactor-arch` skill available at `.claude/skills/refactor-arch/SKILL.md`.
Read the SKILL.md and all reference files, then execute the three phases.

- Phase 1: print the project analysis summary.
- Phase 2: generate the audit report, save it to `../reports/audit-project-3.md`,
  and STOP asking `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]`.
  Do not modify project files before explicit confirmation.
- Phase 3: after confirmation, refactor to MVC and validate boot + all original
  endpoints.

Do not run any git command.
