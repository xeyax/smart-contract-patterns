# Smart Contract Threat Categories

Domain-specific categories for blockchain systems. Used by proposer (to discover risks) and validator (to check coverage).

For each category: if relevant to this project but not addressed → proposer generates R/FR, validator flags gap.

## Categories

1. **Access control** — roles, permissions, privilege escalation, role management, timelock on critical ops
2. **Reentrancy** — external calls callback before state finalized, cross-function, cross-contract read-only
3. **Arithmetic & precision** — rounding direction, decimal handling, dust amounts, overflow in casting
4. **Initialization & upgradeability** — immutable or proxy? storage layout, initialization replay, migration path
5. **Business logic & state transitions** — invariants, atomicity, ordering requirements
6. **Economic attacks** — oracle manipulation, flash loans, MEV/sandwich, incentive misalignment
7. **Denial of service** — unbounded loops, gas griefing, state-locking, one user blocking others
8. **Asset & balance safety** — token flow completeness, emergency withdrawal, stuck funds, accounting invariants
9. **Front-running & MEV** — slippage protection, deadline parameters, ordering-dependent operations
10. **Randomness** — entropy source (if applicable)
11. **Time manipulation** — block.timestamp dependency, tolerance for miner manipulation
12. **External interaction risks** — call failure handling, non-standard tokens (fee-on-transfer, rebasing, ERC-777 hooks, missing return value), protocol upgrade/pause/hack
13. **Chain & ecosystem specific** — target chain, EVM version, L2 sequencer downtime, gas model
14. **Gas efficiency** — gas budgets per operation, block gas limit concerns
15. **Documentation-code alignment** — requirements clear enough to detect implementation mismatch

Skip categories clearly not relevant to the project.

## Severity for financial systems (vaults, lending, DEX)

ERROR if missing:
- #3 Arithmetic & precision — rounding direction MUST be specified for any system handling share calculations or fee calculations
- #6 Economic attacks — deposit/withdrawal MEV protection
- #8 Asset & balance safety — accounting invariants
- #12 External interaction risks — non-standard token handling if system accepts external tokens

WARNING if missing: all other relevant categories.
