# Generate state-machines.md (optional)

You are a subagent generating state-machine diagrams. Fresh context.

## Read

- Tree: `{{DATA_FILE}}`
- Details: `{{DETAILS_DIR}}/AD-*.md`
- Contracts: `{{COMPONENTS_OUTPUT}}`
- Formatting rules: `{{PROFILE_DIR}}/formats/state-machines.md` and `{{PROFILE_DIR}}/formats/mermaid.md`

## Write

`{{OUTPUT}}` — ONLY if the system has entities with discrete state lifecycles.

## When to skip

If no entity has meaningful discrete states (just "active" or stateless), write a one-line file to `{{OUTPUT}}`: `No state machines — system has no entities with discrete lifecycles.` Return `written: {{OUTPUT}} (none)`.

## Task (when applicable)

For each entity with states:
1. States list.
2. Mermaid `stateDiagram-v2`.
3. Transition table: `From | To | Trigger | Guard`.
4. State invariants — what must be true while the entity is in each state.

## Rules

- Only include entities where state transitions are an explicit design decision (not incidental flags).
- If a state or transition cannot be derived from the tree → `[GAP]`.

## Return

`written: {{OUTPUT}}` (inline `[GAP]`/`[CHOICE]` markers go inside the file) or `written: {{OUTPUT}} (none)` when the system has no stateful entities. Use `fatal: <reason>` only if the subagent cannot run at all.
