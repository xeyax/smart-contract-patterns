# Generate threat-coverage.md

You are a subagent generating the threat coverage checklist. Fresh context.

## Domain

{{DOMAIN}}

## Read

- Requirements: `{{DATA_FILE}}`
- Overview: `{{OVERVIEW_OUTPUT}}`
- Boundary map: `{{BOUNDARY_MAP_OUTPUT}}`
- Formatting rules: `{{PROFILE_DIR}}/formats/threat-coverage.md` — **contains the domain-specific threat list**

## Write

`{{OUTPUT}}`

## Task

For every threat in the format rules' threat list, assess whether the requirements address it:

| # | Threat | Status | R-IDs | Notes |
|---|--------|--------|-------|-------|

- **Status** — one of:
  - `COVERED (R-NN)` — a Risk item identifies this threat. (R items in requirements are threat descriptions only, no mitigation.)
  - `ACCEPTED (R-NN)` — Risk item exists with explicit acceptance reasoning.
  - `UNCOVERED [GAP]` — threat is relevant for this system class but no R item describes it.
  - `NOT APPLICABLE` — threat does not apply; one-line justification.
- **R-IDs** — IDs of Risk items linked to this threat.
- **Notes** — what aspect of the threat is captured, what may still be missing.

For each `UNCOVERED [GAP]`: `[GAP]: threat <threat> is relevant per format rules but no R item describes it`.

## Rules

- The threat list is in the profile's format file — that file is THE source of truth for what threats apply to this system class.
- Mark `NOT APPLICABLE` rather than skipping a row — the document should show the full taxonomy.
- Multiple R items may map to one threat (and vice versa).
- Do not invent risks here — only assess existing R items.

## Return

`written: {{OUTPUT}}` (inline `[GAP]`/`[CHOICE]` markers go inside the file). Use `fatal: <reason>` only if the subagent cannot run at all.
