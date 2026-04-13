# Generate plan.md

You are a subagent generating the development plan artifact. Fresh context.

## Read

- Contracts: `{{COMPONENTS_OUTPUT}}`
- Interfaces: `{{INTERFACES_OUTPUT}}`
- Call diagrams: `{{CALL_DIAGRAMS_OUTPUT}}`
- Formatting rules: `{{PROFILE_DIR}}/formats/plan.md`

## Write

`{{OUTPUT}}`

## Task

Development plan derived from contracts, interfaces, and call-diagrams.

1. Task table: `# | Task | Contract | Depends on | Traceable to`.
2. Mermaid dependency graph.

## Rules

- **One task = one bounded unit of work** — implementable and testable in isolation.
- Tasks should cover the full implementation: interfaces, contracts, integration wiring, deploy scripts.
- **Completeness check.** Every contract and every function from `interfaces/*` must map to exactly one task. If not → `[GAP]: <what is uncovered>`.
- "Traceable to" = function name(s) from interfaces, or contract name, or call-diagram section name.

## Return

`written: {{OUTPUT}}` (inline `[GAP]`/`[CHOICE]` markers go inside the file). Use `fatal: <reason>` only if the subagent cannot run at all (missing upstream artifact, unreadable tree).
