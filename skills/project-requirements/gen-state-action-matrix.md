# Generate state-action-matrix.md

You are a subagent generating the state × action matrix. Fresh context.

## Domain

{{DOMAIN}}

## Read

- Requirements: `{{DATA_FILE}}`
- Overview: `{{OVERVIEW_OUTPUT}}`
- Glossary: `{{GLOSSARY_OUTPUT}}`
- Formatting rules: `{{PROFILE_DIR}}/formats/state-action-matrix.md`

## Write

`{{OUTPUT}}`

## Task

Build a matrix:

- **Rows** = state categories **as specified in `{{PROFILE_DIR}}/formats/state-action-matrix.md`**. That file is the authoritative source of which states apply to this system class. If the profile says the system has no applicable states, use the **exact `(none)` wording prescribed by the profile format file** (each profile defines its own phrasing, e.g. "System has only one operational state" or "Library has no stateful entities"). Write that exact line and return `written: {{OUTPUT}} (none)`.
- **Columns** = operations / actions extracted from FR items.
- **Cells** = one of:
  - `works (FR-NN)` — operation allowed in this state, FR-NN defines behavior
  - `blocked (FR-NN)` — explicitly forbidden, FR-NN defines the rejection
  - `undefined` — no FR addresses this state×action pair → `[GAP]`

Below the matrix:

- **Entry/exit conditions** per state — how to enter and how to leave (with FR references).
- For every `undefined` cell: `[GAP]: behavior of <action> in state <state> not defined`.

## Rules

- State list comes from the profile's format file — do NOT invent or import states from other domains. Different profiles have very different state vocabularies (Normal/Paused/Emergency vs. Open/Closed vs. none-at-all).
- One row per state, one column per action. No actions or states skipped.
- A cell can reference multiple FRs if behavior is split.
- If a state is mentioned in Purpose/items but has no entry/exit defined: `[GAP]: state <state> mentioned but no entry/exit conditions`.
- If `requirements.md` mentions a state NOT declared in the profile's format file → do NOT add it as a row. Instead, add a `[CHOICE]` note below the matrix: "state <X> mentioned in requirements but not in profile's state list — not included in matrix. Confirm whether the state model should be extended." The user or gather will decide whether to update the profile or add the state.

## Return

`written: {{OUTPUT}}` (inline `[GAP]`/`[CHOICE]` markers go inside the file) or `written: {{OUTPUT}} (none)` if the system is single-state. Use `fatal: <reason>` only if the subagent cannot run at all.
