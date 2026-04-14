# nfr-coverage.md formatting rules — Python library

## NFR categories (rows)

Library-specific (WHAT-level — the specific mechanism is decided in architecture):
- **API stability** — versioning policy, deprecation, breaking-change rules.
- **Performance** — call latency / throughput / memory footprint targets.
- **Compatibility** — supported Python versions, OS support, dependency constraints.
- **Observability** — diagnostic visibility requirements: what library activity must be inspectable from the outside, at what level of detail. (Logging mechanism, metric hook shape — architecture.)
- **Reliability (resource lifecycle)** — guarantees about when external resources are released, how cleanup behaves on errors, whether re-entry after failure is safe. (Context-manager / finalizer choice — architecture.)
- **Concurrency guarantees** — for any public mutable behavior, statement of which call combinations are safe to run concurrently. (Per-class granularity, lock placement — architecture.)
- **Determinism** — same input → same output guarantees (often essential for libraries).

## Structure

```markdown
# NFR Coverage (Python library)

| Category | Status | Covered by | Notes |
|----------|--------|------------|-------|
| API stability | COVERED | NFR-001 | Stable surface declared; minor-version policy stated |
| Performance | UNCOVERED [GAP] | — | No latency / memory target stated |
| Compatibility | COVERED | NFR-003, C-002 | Python ≥ 3.10, no OS restriction |
| Observability | UNCOVERED [GAP] | — | No diagnostic visibility requirement stated |
| Reliability | COVERED | NFR-004 | Resource lifecycle guarantees on session use |
| Concurrency | UNCOVERED [GAP] | — | Library has shared mutable behavior; no NFR governs concurrent use |
| Determinism | COVERED | NFR-005 | Same input → same output guarantee on processing entry point |

[GAP]: NFR Performance not stated — relevant for any library with non-trivial work
[GAP]: NFR Observability not stated — relevant if user expects to inspect library activity
[GAP]: NFR Concurrency not stated — library has shared mutable behavior
```

## Rules

- Show all 7 categories.
- Concurrency MUST be addressed if the library has any shared mutable behavior.
- Determinism is often implicit — flag if processing/transform-style library lacks the NFR.
