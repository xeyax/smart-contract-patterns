# Generate data-flows.md

You are a subagent generating data flow diagrams. Fresh context.

## Domain

{{DOMAIN}}

"Data" here means whatever units of value or information move through the system: tokens, records, events, messages, API payloads, files. Use the vocabulary the domain expects.

## Read

- Tree: `{{DATA_FILE}}`
- Details: `{{DETAILS_DIR}}/AD-*.md`
- Call diagrams: `{{CALL_DIAGRAMS_OUTPUT}}`
- Formatting rules: `{{PROFILE_DIR}}/formats/data-flows.md` and `{{PROFILE_DIR}}/formats/mermaid.md`

## Write

`{{OUTPUT}}`

## Task

For each meaningful data flow in the system (examples depend on domain: deposit/withdraw/fee/rebalance for a vault; request/response/background-job for a web API; read/transform/write for a pipeline; parse/process/emit for a library):

1. Mermaid `sequenceDiagram` showing movement between actors/components.
2. One-paragraph text summary describing the flow, what it produces, and any transformation or loss along the way.

Max 10 steps per diagram.

## Rules

- Include external systems as participants when data crosses a component boundary.
- If a step is unclear from the tree or call diagrams → `[GAP]`.
- Show where data is transformed, aggregated, dropped, or duplicated. For value flows (tokens, credits) also show who pays fees and where slippage/funding is deducted.

## Return

`written: {{OUTPUT}}` (inline `[GAP]`/`[CHOICE]` markers go inside the file). Use `fatal: <reason>` only if the subagent cannot run at all (missing upstream artifact, unreadable tree).
