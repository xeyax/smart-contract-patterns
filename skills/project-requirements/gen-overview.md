# Generate overview.md

You are a subagent generating the requirements overview. Fresh context.

## Domain

{{DOMAIN}}

## Read

- Requirements: `{{DATA_FILE}}` — full file with Purpose + items
- Formatting rules: `{{PROFILE_DIR}}/formats/overview.md`

## Write

`{{OUTPUT}}`

## Task

One short artifact (≤ 1 page) with three blocks:

1. **What & for whom** — 2–3 sentences derived from the Purpose section.
2. **Context** — standalone system or part of a larger one. If part of a larger system, name the larger system and the component's role.
3. **External dependencies** — bulleted list of every external system / protocol / oracle / library mentioned in Purpose or Constraints. Each bullet: name + one-line role.

## Rules

- **Pull from Purpose first**, then from explicit Constraint (C) items.
- If Purpose is missing → write `[GAP]: Purpose section missing or empty`.
- If an external dependency is mentioned in FRs but not in Purpose/C → list it under "External dependencies" and mark `[GAP]: dependency X used by FR-NN but not declared in Purpose or Constraints`.

## Return

`written: {{OUTPUT}}` (inline `[GAP]`/`[CHOICE]` markers go inside the file). Use `fatal: <reason>` only if the subagent cannot run at all.
