# Generate nfr-coverage.md

You are a subagent generating the NFR coverage checklist. Fresh context.

## Domain

{{DOMAIN}}

## Read

- Requirements: `{{DATA_FILE}}`
- Overview: `{{OVERVIEW_OUTPUT}}`
- Formatting rules: `{{PROFILE_DIR}}/formats/nfr-coverage.md`

## Write

`{{OUTPUT}}`

## Task

For each NFR category from the format rules (typical: Security, Performance, Compatibility, Upgradeability, Observability, Reliability — profile may extend), assess coverage:

| Category | Status | Covered by | Notes |
|----------|--------|------------|-------|

- **Status** — one of:
  - `COVERED` — at least one NFR addresses this category.
  - `UNCOVERED [GAP]` — category is relevant for this system class (per format rules) but no NFR exists.
  - `NOT APPLICABLE` — category does not apply to this kind of system; one-line justification.
- **Covered by** — list of NFR-IDs.
- **Notes** — what specifically is covered, what aspect of the category may still be missing.

For each `UNCOVERED [GAP]`: `[GAP]: NFR category <category> is relevant for this system class but no NFR addresses it`.

## Rules

- Use the category list from the profile's format file (it knows which are relevant for this domain).
- Do not invent NFRs — only assess what already exists.
- Coverage is binary at category level; nuance goes into Notes.

## Return

`written: {{OUTPUT}}` (inline `[GAP]`/`[CHOICE]` markers go inside the file). Use `fatal: <reason>` only if the subagent cannot run at all.
