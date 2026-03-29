# Token Flows Formatting Rules

Rules for `token-flows.md` artifact. Also see `mermaid.md` for general mermaid rules.

## Structure

One `##` section per flow. Each section contains:
1. `sequenceDiagram` mermaid block
2. One-paragraph text summary below the diagram

## Diagram style

- Use plain arrows with inline action descriptions: `A->>B: action(params)`.
- Use `Note over X:` for postconditions, consistently across all flows (not `Note right of`).
- `->>` for calls, `-->>` for returns/transfers.
- Max 10 steps per diagram.
