# Generate glossary.md

You are a subagent generating the requirements glossary. Fresh context.

## Domain

{{DOMAIN}}

## Read

- Requirements: `{{DATA_FILE}}`
- Overview (for consistency): `{{OVERVIEW_OUTPUT}}`
- Formatting rules: `{{PROFILE_DIR}}/formats/glossary.md`

## Write

`{{OUTPUT}}`

## Task

Enumerate every domain-specific term used in `requirements.md` and Purpose/Context with a one-line definition.

Sources for definitions, in order:
1. Explicit definitions in Purpose, Context, or Glossary section (if exists).
2. Inferred from how the term is used in items (FR/NFR/C/R) — mark `[CHOICE]: definition inferred from usage`.
3. Term used but no source explains it → entry with definition "—" + `[GAP]: term X used in FR-NN, no definition`.

Do NOT include:
- Generic English words (`user`, `system`, `operation`).
- Standard technical names that are unambiguous in context (`HTTP`, `JSON`, `ERC-20`).

## Rules

- One row per term.
- Group alphabetically (or by domain section if format rules say so).
- A term can be a noun, role name, state name, or domain concept.
- If two FRs use the same term differently → add `[CHOICE]: term has multiple uses; current definition picks one`.

## Return

`written: {{OUTPUT}}` (inline `[GAP]`/`[CHOICE]` markers go inside the file). Use `fatal: <reason>` only if the subagent cannot run at all.
