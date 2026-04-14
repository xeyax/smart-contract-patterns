# threat-coverage.md formatting rules — Python library

## Threat list (rows)

Library-specific threats:

| # | Threat | Applies when |
|---|--------|--------------|
| 1 | Unintended breaking change on stable API | Library has stable surface |
| 2 | Thread safety violation | Library has mutable global / class-level state |
| 3 | Resource leak (file handle / socket / subprocess / lock) | Library opens external resources |
| 4 | Pickle / marshal / eval on untrusted data | Library serializes/deserializes user-supplied data |
| 5 | Subprocess command injection | Library spawns processes with user input |
| 6 | Path traversal | Library reads/writes user-supplied paths |
| 7 | Dependency drift / vulnerability | Library has runtime dependencies |
| 8 | Monkey-patching side-effects | Library mutates third-party module state |
| 9 | Locale / encoding bug | Library handles text I/O |
| 10 | Logging leakage (secrets in logs) | Library logs user-provided data |
| 11 | Signal / atexit handler interference | Library registers handlers |
| 12 | Surprising semantics on public classes (attribute access, subclassing, copy/pickle) | Library exposes classes users may subclass, pickle, or attribute-set |
| 13 | Import cycle / name shadow | Non-trivial package structure |
| 14 | Unbounded input → memory exhaustion | Library accepts user input of arbitrary size |
| 15 | Documentation-code drift | Always |

## Structure

```markdown
# Threat Coverage (Python library)

| # | Threat | Status | R-IDs | Notes |
|---|--------|--------|-------|-------|
| 1 | Unintended breaking change | COVERED | R-001 | Stability policy stated |
| 2 | Thread safety violation | UNCOVERED [GAP] | — | Library has shared cache, no R describes concurrency risk |
| 3 | Resource leak | COVERED | R-003 | File handle ownership defined via context manager |
| 4 | Pickle / eval on untrusted data | NOT APPLICABLE | — | Library does not deserialize user data |
| 5 | Subprocess command injection | NOT APPLICABLE | — | No subprocess use |
| ... |

[GAP]: threat "Thread safety violation" relevant — library has shared cache, but no R item
[GAP]: threat "Unbounded input" relevant — library accepts arbitrary string input
```

## Rules

- Show all 15 rows. NOT APPLICABLE rows include one-line justification.
- WHAT-level only: do not require specific mechanisms (lock, weakref, sandbox) — those are architecture decisions.
- Library-specific: thread safety + resource leak + breaking change are the most common gaps; flag aggressively.
