# Smart Contract Threat Categories

Domain-specific categories for blockchain systems. Used by proposer (to discover risks) and validator (to check coverage).

For each category: if relevant to this project but not addressed → proposer generates R item (with WHAT-level mitigation), validator flags gap.

IMPORTANT: categories describe WHAT must be protected, not HOW. Do not require specific mechanisms (timelock, TWAP, ReentrancyGuard) in requirements — those are architecture decisions.

## Categories

Descriptions below are WHAT-level: what must be protected / prevented. HOW to protect = architecture.

1. **Access control** — restricted operations can only be performed by authorized parties. Unauthorized callers are rejected.
2. **Reentrancy** — no external call can cause the system to enter an inconsistent state by re-entering during execution.
3. **Arithmetic & precision** — rounding direction specified, no exploitable precision loss, no value extraction through repeated operations.
4. **Initialization & upgradeability** — system's upgradeability model is explicitly decided (immutable or upgradeable with safeguards). Initialization cannot be replayed.
5. **Business logic & state transitions** — system invariants stated, operations are atomic, state transitions are complete and well-defined.
6. **Economic attacks** — system is not exploitable via price manipulation, flash loans, or same-block value extraction.
7. **Denial of service** — no single user can block others from using the system.
8. **Asset & balance safety** — all token flows accounted for, funds cannot get stuck, emergency exit exists.
9. **Front-running & MEV** — users can specify acceptable worst-case terms for value-bearing operations.
10. **Randomness** — if randomness needed, it cannot be predicted or controlled by participants.
11. **Time manipulation** — system behavior is not exploitable via minor time variations.
12. **External interaction risks** — system handles failures of external dependencies and non-standard token behaviors.
13. **Chain & ecosystem specific** — target chain and its constraints are explicitly stated.
14. **Gas efficiency** — operations remain economically viable for users.
15. **Documentation-code alignment** — requirements are specific enough to detect implementation mismatch.

Skip categories clearly not relevant to the project.

## Severity for financial systems (vaults, lending, DEX)

ERROR if missing:
- #3 Arithmetic & precision — rounding direction MUST be specified for any system handling share calculations or fee calculations
- #6 Economic attacks — deposit/withdrawal MEV protection
- #8 Asset & balance safety — accounting invariants
- #12 External interaction risks — non-standard token handling if system accepts external tokens

WARNING if missing: all other relevant categories.
