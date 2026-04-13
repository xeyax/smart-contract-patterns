# Generate invariants.md

You are a subagent generating the invariants artifact. Fresh context.

## Read

- Tree: `{{DATA_FILE}}`
- Details: `{{DETAILS_DIR}}/AD-*.md`
- Components: `{{COMPONENTS_OUTPUT}}`
- Data flows (if present): `{{DATA_FLOWS_OUTPUT}}` — for conservation properties
- Access control (if present): `{{ACCESS_CONTROL_OUTPUT}}` — for always-true access-control constraints
- State machines (if present): `{{STATE_MACHINES_OUTPUT}}` — for per-state constraints
- Formatting rules: `{{PROFILE_DIR}}/formats/invariants.md`

Empty placeholder = profile skipped that entry — skip the read.

## Write

`{{OUTPUT}}`

## Task

For each contract, enumerate what must ALWAYS be true after ANY sequence of valid calls.

Format: one invariant per line, plain English, grouped by contract.

## Sources of invariants

- Explicit `Formula` or `Assumptions` sections in detail files (`AD-NNN-*.md`).
- Conservation properties implied by data-flows (for Solidity: sum of user balances == totalSupply; for other domains: no records created or lost across a transformation, etc.).
- Access-control constraints that are always true (role assignments are unique, etc.).
- State-machine constraints (entity cannot be in two states, etc.).

## Rules

- **One invariant = one line.** Plain English.
- **Exclude platform guarantees** (EVM atomicity, overflow protection in 0.8+, msg.sender identity).
- **Exclude preconditions** — invariants are post-any-call truths, not input validations.
- If an invariant is implied by the tree but not explicit → include it and mark `[CHOICE]` at end of the line explaining the interpretation.

## Return

`written: {{OUTPUT}}` (inline `[GAP]`/`[CHOICE]` markers go inside the file). Use `fatal: <reason>` only if the subagent cannot run at all (missing upstream artifact, unreadable tree).
