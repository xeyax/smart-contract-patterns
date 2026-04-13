# Generate call-diagrams.md

You are a subagent generating architecture call diagrams. Fresh context.

## Read

- Tree: `{{DATA_FILE}}`
- Details: `{{DETAILS_DIR}}/AD-*.md`
- Contracts: `{{COMPONENTS_OUTPUT}}`
- Interfaces: `{{INTERFACES_OUTPUT}}`
- Formatting rules: `{{PROFILE_DIR}}/formats/call-diagrams.md` and `{{PROFILE_DIR}}/formats/mermaid.md`

## Write

`{{OUTPUT}}`

## Task

Sequence diagrams for **every key operation** in the system — not only value flows. Admin, keeper, governance, emergency, migration all count.

Identify operations: every `✓` AD node that describes an action or process gets a diagram.

For each operation:
- One section with a mermaid `sequenceDiagram`.
- After each significant step, a `POST:` line describing the observable postcondition (balance delta, state change, event emitted). These become test assertions in specs.

## This is the key verification artifact

If you cannot draw the full call chain with postconditions, the architecture is underspecified → `[GAP]`.

## Rules

- Only use function names present in `interfaces/*`. If an operation requires a call that has no matching signature → `[GAP]: call X on Y not in interface`.
- Max ~10 steps per diagram. Split long operations into sub-diagrams.
- POST lines are quantitative when possible (`user.balance += amount`, `totalSupply increased by shares`).

## Return

`written: {{OUTPUT}}` (inline `[GAP]`/`[CHOICE]` markers go inside the file). Use `fatal: <reason>` only if the subagent cannot run at all (missing upstream artifact, unreadable tree).
