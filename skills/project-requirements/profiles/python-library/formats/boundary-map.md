# boundary-map.md formatting rules

## Structure

```markdown
# Boundary Map

## A. Runtime external interactions

| Dependency | Kind | Declared by C | Used by FRs | Failure mode | Status |
|------------|------|---------------|-------------|--------------|--------|
| Configuration file (user-supplied path) | runtime | C-003 | FR-007 | — | [GAP]: no failure mode |
| Subprocess invocation for external tool | runtime | C-005 | FR-001, FR-002 | R-004 (tool missing or non-zero exit) | complete |
| HTTP endpoint (optional telemetry) | runtime | — | FR-010 | — | [GAP]: declared neither, two gaps |

## B. Environment / build-time / packaging constraints

| Constraint | Kind | Declared by C/NFR | Notes |
|------------|------|--------------------|-------|
| Supported Python ≥ 3.X | environment | C-001 | Single-version target |
| Allowed runtime packages | environment | NFR-007 | List in NFR-007 (no heavy deps; stdlib-only preferred) |
| Supported OS platforms | environment | C-002 | Linux + macOS (Windows best-effort) |
| Required env vars | environment | C-004 | `MYLIB_CONFIG_PATH`, `MYLIB_LOG_LEVEL` |
| Build toolchain | environment | — | [GAP]: build tool mentioned in Purpose, no C |

## Boundary violations

- FR-NN describes external behavior ("config file is UTF-8 encoded") — should be a Constraint, not an FR.
  [GAP]: FR-NN describes external behavior, should be C
```

If empty:
```markdown
# Boundary Map

System has no external dependencies — fully self-contained.
```

## Rules

- Two sections always present (A and B). If a section has no rows, write a one-line note.
- Section A (runtime): three columns required (C, Used by FRs, Failure mode). Each empty → `[GAP]`.
- Section B (environment): only "Declared by C/NFR" required.
- Ambiguous classification → Section A + `[CHOICE]` line in Notes / Status.
- Each FR demanding behavior from an external system → "Boundary violations" entry.
