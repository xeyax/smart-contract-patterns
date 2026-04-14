# Generate participant-matrix.md

You are a subagent generating the participant × action matrix. Fresh context.

## Domain

{{DOMAIN}}

## Read

- Requirements: `{{DATA_FILE}}`
- Overview: `{{OVERVIEW_OUTPUT}}`
- Glossary: `{{GLOSSARY_OUTPUT}}`
- Formatting rules: `{{PROFILE_DIR}}/formats/participant-matrix.md`

## Write

`{{OUTPUT}}`

## Task

Build a matrix:

- **Rows** = abstract participant categories. For most systems: Users (unprivileged), Privileged roles (configuration / emergency / restricted ops), Permissionless callers (open to anyone), External systems (oracles, base protocols, sibling components). Add or remove categories that the profile's format rules specify.
- **Columns** = distinct actions / capabilities mentioned across FR items.
- **Cells** = list of FR-IDs that grant this category this action. Empty cell = participant category implied by Purpose but no FR covers this action.

Below the matrix:

- **Coverage notes** — per row: which actions covered, which implied but missing.
- For every empty cell where the participant category is referenced in Purpose: `[GAP]: <category> implied in Purpose but no FR for action <action>`.
- For every participant category referenced in Purpose with NO FRs at all: `[GAP]: <category> mentioned but has no requirements`.

## Rules

- Use abstract categories, not specific role names ("privileged" not "owner").
- Pull categories from the profile's format file — they encode domain conventions.
- One FR may appear in multiple cells if it grants multiple categories the same capability.
- Skip categories not applicable to this system (note in coverage notes).

## Return

`written: {{OUTPUT}}` (inline `[GAP]`/`[CHOICE]` markers go inside the file). Use `fatal: <reason>` only if the subagent cannot run at all.
