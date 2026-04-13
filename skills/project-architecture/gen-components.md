# Generate components.md

You are a subagent generating a single architecture artifact. Fresh context — you have been given only what you need.

## Domain

{{DOMAIN}}

The term "component" maps to the unit of decomposition for this domain: smart contracts, Python modules/packages, TypeScript services, etc. Use the vocabulary specified in `{{PROFILE_DIR}}/formats/components.md`.

## Read

- Tree: `{{DATA_FILE}}`
- Details: `{{DETAILS_DIR}}/AD-*.md`
- Requirements: `{{REQUIREMENTS_FILE}}` (if provided)
- Overview (for consistency): `{{OVERVIEW_OUTPUT}}`
- Formatting rules: `{{PROFILE_DIR}}/formats/components.md`

## Write

`{{OUTPUT}}`

## Task

Decompose the system into components:

1. **Responsibility table**: `Component | Responsibility | Depends on`.
2. **Mermaid interaction graph**: components as boxes, external systems in brackets `[Name]`, actors/roles as plain text. Max 15 nodes.
3. **State per component**: high-level names + one-line descriptions + mutability (`immutable`, `mutable`, `set once`). No concrete language types — that lives in interfaces.

## Rules

- **Responsibility = one clear sentence.** If you cannot write it clearly → `[GAP]`.
- **Only confirmed decisions** (`✓` AD). Ignore `→`, `?`.
- **No function signatures, no concrete types** — architecture-level only.
- `[GAP]` if a component's responsibility is undecided. `[CHOICE]` if multiple valid decompositions exist and the tree does not pick one.

## Return

`written: {{OUTPUT}}` (inline `[GAP]`/`[CHOICE]` markers go inside the file). Use `fatal: <reason>` only if the subagent cannot run at all (missing upstream artifact, unreadable tree).
