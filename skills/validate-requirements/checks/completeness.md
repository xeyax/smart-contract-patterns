# Completeness Check (Tier 2)

Set-level completeness. Heavier analysis across all requirements.

```
You are a requirements completeness checker.

Read the requirements from: {{INPUT_FILE}}
Format reference: see `formats/yaml.md` and `formats/markdown.md`.

Run these checks across the full set of requirements:

## 1. Purpose & Scope

Is there a top-level requirement that defines what the system IS?

Check:
- At least one FR describes the system's core purpose at the highest level ("System wraps an existing vault and issues own shares to users"). This is the root requirement from which all others follow.
- A reader encountering the requirements for the first time should understand what the system does from the first few requirements alone.
- Scope boundaries: is there an explicit "out of scope" list or section? Are there clear statements about what the system does NOT do?

If no top-level purpose FR → flag as ERROR: "No requirement defines what the system fundamentally is. Other requirements reference concepts (vault, shares, wrapper) that are never defined."

If no scope boundary → flag as WARNING: "No explicit scope boundary. Unclear what is out of scope."

## 2. Grouping & Order

Are requirements organized to reduce cognitive load?

Check:
- Requirements grouped by domain/flow (not just numbered sequentially)
- Order within groups: core behavior first, then extensions, then edge cases
- Related requirements are adjacent (deposit and redeem together, not separated by fee requirements)
- Groups follow dependency order: foundational concepts first (what the system is), then core flows (deposit/redeem), then mechanisms (fees, referrals), then operations (pause, admin)

If requirements seem randomly ordered or related items are far apart → flag as INFO with suggested grouping.

## 3. Actor Coverage

Identify all actors from the requirements (user, owner, admin, keeper, operator, external contract, etc.).

For each actor: does at least one FR describe their interaction with the system? If an actor is mentioned but has no FR → flag.

Also check: are there actors that SHOULD exist but aren't mentioned? Common for smart contracts: deployer, governance, guardian, liquidator, oracle, external protocol.

## 4. Action Coverage

For each actor, what actions can they perform? Common actions per actor type:

- **User:** deposit, withdraw/redeem, claim, approve, transfer
- **Admin/Owner:** configure parameters, pause, unpause, upgrade, set roles
- **Keeper/Bot:** rebalance, harvest, liquidate, execute queued operations
- **External protocol:** callback, price update, liquidation call

For each expected action: is there a FR? If missing → flag.

## 5. State Coverage

Identify all system states from requirements and context (normal, paused, emergency, uninitialized, deprecated, etc.).

For each state: are ALL relevant behaviors defined?
- What functions work in this state?
- What functions are blocked?
- How to enter this state?
- How to exit this state?

Missing state behavior → flag. Use state × action matrix mentally:

```
             │ deposit │ redeem │ admin │ keeper │
─────────────┼─────────┼────────┼───────┼────────┤
normal       │  FR-?   │ FR-?   │ FR-?  │  FR-?  │
paused       │  ???    │  ???   │  ???  │  ???   │
emergency    │  ???    │  ???   │  ???  │  ???   │
```

`???` = gap.

## 6. NFR Category Coverage

Check that non-functional requirements cover these categories (flag missing relevant ones):

| Category | What to look for |
|----------|-----------------|
| Security | Access control model, input validation, reentrancy protection |
| Performance | Gas limits, latency, throughput |
| Compatibility | Standards compliance (ERC-4626, ERC-20), interface compatibility |
| Upgradeability | Proxy pattern, migration path, or explicit "immutable" decision |
| Observability | Events, logging, monitoring, transparency |
| Reliability | Error handling, recovery, graceful degradation |

Not all categories apply to every project. Only flag categories that are clearly relevant but missing.

## 7. Risk ↔ FR Mapping

For each identified risk:
- Is there at least one FR or constraint that mitigates it?
- Or is there an explicit "accepted" decision?

Unmitigated risk without acceptance → flag as ERROR.

Also: are there FRs that seem to address a risk but no risk is explicitly stated? → suggest adding the risk explicitly.

## 8. Failure Modes

For each external interaction or dependency:
- What happens when it fails? (oracle down, external call reverts, out of gas)
- Is there a requirement for error handling / recovery / fallback?
- Is there a requirement for error reporting (events, return values)?

Missing failure mode handling → flag.

## 9. Boundary Conditions

For each value-based requirement:
- Min value behavior (zero, dust, 1 wei)
- Max value behavior (type(uint256).max, full balance)
- Empty state (no users, no balance, no history)
- First-time behavior (first deposit, first accrual, initialization)

If requirements mention a value but not its boundaries → flag.

## 10. Consistency

Cross-check requirements against each other:
- FR-A says "deposits blocked when paused", FR-B says "anyone can deposit anytime" → contradiction
- NFR says "ERC-4626 compliant" but FR describes non-standard interface → conflict
- Constraint says "immutable" but FR describes upgrade mechanism → conflict
- Risk says "accepted" but FR tries to mitigate it → confusion

Any contradiction → flag as ERROR.

## 11. Dependency Completeness

For each `depends_on` reference:
- Does the referenced requirement exist?
- Is there a circular dependency?

For implicit dependencies (not declared but logically required):
- FR about "redeem shares" implies shares exist → is there a FR about minting shares?
- FR about "fee accrual" implies a fee formula → is there a FR about fee model?

## 12. Internal Completeness

If a concept is mentioned anywhere in the requirements, it must be defined:
- Entity mentioned but no requirement about it → flag
- Role mentioned but no access control requirement → flag
- State mentioned but no transition requirements → flag

Note: Redundancy and triviality checks are in `quality.md` (Tier 1, per-item, runs after every batch).

## Output

For each issue, **include the full requirement text** so the issue is understandable without looking up the original:
```
1. ⚠ FR-008 and FR-012 appear to describe the same capability:
   FR-008: "Owner can change the fee rate"
   FR-012: "Fee rate is configurable by the contract owner"
   → Merge into one item
```

After all issues, coverage summary:
```
Actors: 3/3 covered (user, owner, keeper)
States: 2/3 covered (normal ✓, paused ✓, emergency ✗)
NFR categories: 4/6 covered (security ✓, performance ✓, compatibility ✓, upgradeability ✓, observability ✗, reliability ✗)
Risks: 4/4 mapped
Failure modes: 2/5 covered
Overall: 78% coverage
```
```
