# state-action-matrix.md formatting rules — Python library

## State categories (rows)

Most libraries are mostly stateless. Default minimal set:

- **Open** — Session/handle/context active, normal use.
- **Closed** — after `.close()` / context-manager exit; further use raises typed exception.

Add domain states only if the tree has explicit lifecycle (e.g. `Streaming`, `Buffered`, `Drained`, `ConfigLoaded vs ConfigUnloaded`). If no entity has stateful lifecycle beyond Open → write a one-line file: "Library has no stateful entities — no state×action matrix needed." and return `written: {{OUTPUT}} (none)`.

## Structure

```markdown
# State × Action Matrix (Python library)

| State \ Action | parse() | close() | reset() | as context manager |
|----------------|---------|---------|---------|--------------------|
| Open           | works (FR-002) | works (FR-004) | works (FR-005) | works (FR-001) |
| Closed         | raises SessionClosedError (FR-002 AC) | works idempotent (FR-004) | undefined | — |

## State entry / exit

- **Open** → enter on Session() construction (FR-001); exit on .close() (FR-004) or context exit.
- **Closed** → enter via close() / context exit; never re-enter (Sessions are single-use).

## Gaps

[GAP]: behavior of reset() when Closed is not defined
```

## Rules

- Use lifecycle states only if the library actually has them.
- Cell values: `works (FR-NN)`, `raises X (FR-NN AC)`, `undefined`, or `—` (action not relevant).
- Idempotency-relevant cells should explicitly say `works idempotent` if the contract demands it.
