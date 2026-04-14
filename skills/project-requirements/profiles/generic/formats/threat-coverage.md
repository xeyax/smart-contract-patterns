# threat-coverage.md formatting rules — generic

## Threat list (rows)

Generic system-class threats. Profile-specific overrides (solidity, python-library) replace this list with domain-specific items.

| # | Threat | Applies when |
|---|--------|--------------|
| 1 | Unauthorized access | System has restricted operations |
| 2 | Input validation failure | System accepts external input |
| 3 | Race condition / concurrency | System has concurrent users / threads |
| 4 | Resource exhaustion (DoS) | System has bounded resources |
| 5 | External dependency failure | System depends on external systems |
| 6 | Data corruption / inconsistency | System holds persistent state |
| 7 | Information disclosure | System handles sensitive data |
| 8 | Replay / duplicate processing | System processes stateful operations |
| 9 | Privilege escalation | System has multiple privilege levels |
| 10 | Configuration error | System has configurable behavior |

## Structure

```markdown
# Threat Coverage

| # | Threat | Status | R-IDs | Notes |
|---|--------|--------|-------|-------|
| 1 | Unauthorized access | COVERED | R-001 | Caller authentication required |
| 2 | Input validation failure | COVERED | R-002 | All entry-point inputs validated |
| 3 | Race condition | NOT APPLICABLE | — | Single-threaded library |
| 4 | Resource exhaustion | UNCOVERED [GAP] | — | System accepts user input but no bound on size mentioned |
| 5 | External dependency failure | COVERED | R-005 | |
| ... |

[GAP]: threat "Resource exhaustion (DoS)" is relevant per generic threat list but no R item describes it
```

## Rules

- Show the full table (NOT APPLICABLE rows included).
- Status: `COVERED`, `ACCEPTED`, `UNCOVERED [GAP]`, `NOT APPLICABLE`.
- Each `UNCOVERED [GAP]` → matching `[GAP]:` line.
- This is a generic baseline. Profile-specific format files override with domain threats (smart-contract has 15, python-library has lib-specific list).
