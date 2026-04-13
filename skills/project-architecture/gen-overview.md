# Generate overview.md

You are a subagent generating a single architecture artifact. Fresh context — you have been given only what you need.

## Read

- Tree file: `{{DATA_FILE}}` — architecture decision tree
- All detail files matching `{{DETAILS_DIR}}/AD-*.md`
- Requirements file (if provided): `{{REQUIREMENTS_FILE}}`
- Formatting rules: `{{PROFILE_DIR}}/formats/overview.md`

## Write

`{{OUTPUT}}`

## Task

Produce a concise architecture overview:

1. **What / for whom / on which chain** — 2–3 sentences. Derived from Purpose (requirements) and top-level AD decisions.
2. **Key architectural decisions** — bulleted list from top-level `✓ AD` nodes. Each bullet: one-line decision + one-line rationale. These are ADR candidates.

## Rules

- **Only ✓ nodes.** Skip `→` suggested and `?` open decisions.
- **Plain language.** No function signatures, no Solidity types, no formulas.
- `[GAP]` if Purpose is missing or empty. `[CHOICE]` if multiple top-level decisions contradict and the tree does not resolve it.
- Do not invent. Only use what is in tree + details + requirements.

## Return

Short status: `written: {{OUTPUT}}` (inline `[GAP]`/`[CHOICE]` markers go inside the file). Use `fatal: <reason>` only if the subagent cannot run at all (missing upstream artifact, unreadable tree).
