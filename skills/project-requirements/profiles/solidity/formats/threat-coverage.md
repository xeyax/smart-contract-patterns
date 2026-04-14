# threat-coverage.md formatting rules — Solidity smart contracts

## Threat list (rows) — 15 categories

From `validate-requirements/rules/smart-contract-threats.md`:

| # | Threat | Applies when |
|---|--------|--------------|
| 1 | Access control | System has restricted operations |
| 2 | Reentrancy | System makes external calls |
| 3 | Arithmetic & precision | System handles share / fee calculations |
| 4 | Initialization & upgradeability | Always |
| 5 | Business logic & state transitions | System has invariants and stateful operations |
| 6 | Economic attacks (MEV, flash loans, price manipulation) | System handles value transfers |
| 7 | Denial of service | System has bounded actions per user |
| 8 | Asset & balance safety | System holds assets |
| 9 | Front-running & MEV | System has value-bearing operations |
| 10 | Randomness | System needs unpredictability |
| 11 | Time manipulation | System depends on block.timestamp |
| 12 | External interaction risks | System integrates external protocols / non-standard tokens |
| 13 | Chain & ecosystem specific | Always (chain choice + constraints) |
| 14 | Gas efficiency | System has user-facing operations |
| 15 | Documentation-code alignment | Always |

## Severity for financial systems (vaults, lending, DEX)

ERROR if missing: #3 (rounding direction not specified), #6 (MEV protection), #8 (accounting invariants), #12 (non-standard token handling).
WARNING if missing: all other relevant categories.

## Structure

```markdown
# Threat Coverage (Solidity)

| # | Threat | Status | R-IDs | Notes |
|---|--------|--------|-------|-------|
| 1 | Access control | COVERED | R-001 | Privileged ops gated |
| 2 | Reentrancy | COVERED | R-004 | All entry points marked |
| 3 | Arithmetic & precision | UNCOVERED [GAP] | — | Share rounding direction not specified — ERROR for vault systems |
| 4 | Initialization & upgradeability | COVERED | R-005 | Immutable, no initializer replay |
| 5 | Business logic & state transitions | COVERED | R-006 | Invariants stated |
| 6 | Economic attacks | UNCOVERED [GAP] | — | Same-block deposit MEV not addressed — ERROR for vaults |
| ... |

[GAP]: threat "Arithmetic & precision" is critical for this system class but no R item describes rounding direction
[GAP]: threat "Economic attacks" critical for vault — no MEV protection R
```

## Rules

- Show all 15 rows. NOT APPLICABLE rows include one-line justification.
- For financial systems, mark ERROR-level missing categories explicitly in Notes.
- WHAT-level only: do not require specific mechanisms (timelock, TWAP, ReentrancyGuard) in requirements — those are architecture decisions.
- Requirements-level risks are GENERIC; architecture-specific risks (e.g. "Aave may liquidate") belong in the architecture tree, not here.
