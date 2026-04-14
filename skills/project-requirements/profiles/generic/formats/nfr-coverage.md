# nfr-coverage.md formatting rules

## NFR categories (rows)

Default categories applicable to most software:
- **Security** — auth, isolation, input validation, secret handling.
- **Performance** — latency, throughput, resource usage limits.
- **Compatibility** — interfaces, standards, backwards-compat guarantees.
- **Upgradeability** — version migration, schema evolution, feature flags.
- **Observability** — logging, metrics, traces, debug surfaces.
- **Reliability** — fault tolerance, recovery, degradation behavior.

Profile may override or extend.

## Structure

```markdown
# NFR Coverage

| Category | Status | Covered by | Notes |
|----------|--------|------------|-------|
| Security | COVERED | NFR-001, NFR-003 | Auth + input validation; no secret-handling NFR yet |
| Performance | COVERED | NFR-002 | Throughput target only; latency not specified |
| Compatibility | UNCOVERED [GAP] | — | System exposes a versioned API per Purpose, no NFR governs compatibility |
| Upgradeability | NOT APPLICABLE | — | One-shot tool, no upgrade path |
| Observability | UNCOVERED [GAP] | — | No NFR for logs/metrics |
| Reliability | COVERED | NFR-004 | Recovery after process restart specified |

[GAP]: NFR category Compatibility is relevant for this system class but no NFR addresses it
[GAP]: NFR category Observability is relevant for this system class but no NFR addresses it
```

## Rules

- Show the full category list, even NOT APPLICABLE rows (justifies omission).
- Status values: `COVERED`, `ACCEPTED` (rare), `UNCOVERED [GAP]`, `NOT APPLICABLE`.
- Each `UNCOVERED [GAP]` → matching `[GAP]:` line below the table.
