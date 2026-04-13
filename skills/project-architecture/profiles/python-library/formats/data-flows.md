# Data Flows Formatting Rules (Python library)

Rules for the `data-flows.md` artifact when the target is a Python library. "Data" here means the **records, events, API payloads, configs, streams, files, and return values** that move between library modules and between the library and its user. Not tokens — this is not a value-transfer system.

Typical flows for a library:
- Input parsing flow (raw input → validated structure → internal representation)
- Query/response flow (user call → internal pipeline → return value)
- Streaming / iterator flow (source → transform → consumer)
- Side-effect flow (user call → external resource read/write → library state update)
- Error propagation flow (internal failure → typed exception → user boundary)

Also see `mermaid.md` for general mermaid rules.

## Structure

One `##` section per flow. Each section contains:
1. `sequenceDiagram` mermaid block
2. One-paragraph text summary below the diagram describing what moves, where it is transformed, and what the user observes

## Diagram style

- Use plain arrows with inline action descriptions: `A->>B: action(params)`.
- Use `Note over X:` for postconditions, consistently across all flows (not `Note right of`).
- `->>` for calls, `-->>` for returns.
- Represent external resources (filesystem, network, subprocess) as participants with bracketed names: `[filesystem]`, `[subprocess]`.
- Max 10 steps per diagram.

## Rules

- Show where data is transformed, validated, cached, or discarded.
- Show where typed exceptions are raised in the flow (label the arrow with the exception name).
- If a flow reads or writes an external resource, mark the boundary — helpful for later risk review (resource leaks, exception paths).
- `[GAP]` if a step is unclear from the tree or call diagrams.
