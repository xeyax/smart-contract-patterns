# Completeness Criteria

Set-level checks. Used by proposer (to find what to generate) and validator (to find what's missing).

For each criterion: if gap found → proposer generates item, validator flags issue.

## 1. Purpose & Scope

Criterion: at least one item defines what the system IS. Explicit in-scope and out-of-scope lists exist.

Gap: no top-level purpose → reader can't understand what the system does.

## 2. Grouping & Order

Criterion: items grouped by domain/flow. Order: core → extensions → operations. Related items adjacent.

Gap: items randomly ordered, related items far apart → cognitive load.

## 3. Actor Coverage

Criterion: every actor mentioned or implied has ≥1 FR.

Common actors: user, owner, admin, keeper, operator, external protocol, system/time.

Gap: actor mentioned but no FR describes their interaction.

## 4. Action Coverage

Criterion: for each actor, all expected actions have FRs.

Common actions per actor:
- User: deposit, withdraw/redeem, claim, approve
- Admin/Owner: configure parameters, pause, set roles
- Keeper: rebalance, harvest, liquidate, execute queued ops
- External: callback, price update

Gap: expected action for an actor has no FR.

## 5. State Coverage

Criterion: for each system state (normal, paused, emergency, uninitialized), ALL relevant behaviors defined.

For each state: what works? what's blocked? how to enter? how to exit?

Gap: state exists but behavior for some functions undefined in that state.

## 6. NFR Category Coverage

Criterion: each relevant category addressed.

Categories: security, performance, compatibility, upgradeability, observability, reliability.

Gap: category clearly relevant but no NFR for it.

## 7. Risk ↔ FR Mapping

Criterion: every risk has ≥1 mitigating FR or explicit "accepted" decision.

Gap: unmitigated risk without acceptance.

## 8. Failure Modes

Criterion: for each external dependency, failure handling described.

What happens when: oracle down, external call reverts, out of gas, protocol paused?

Gap: external dependency without failure mode requirement.

## 9. Boundary Conditions

Criterion: for each value-based requirement, boundary behavior specified.

Check: zero, dust, first-time, maximum, empty state.

Gap: value mentioned but boundaries not specified.

## 10. Consistency

Criterion: no contradictions between items.

Check: FR vs FR, NFR vs FR, constraint vs FR, risk mitigation vs acceptance.

Gap: two items contradict each other.

## 11. Dependency Completeness

Criterion: referenced items exist, no circular dependencies.

Check: implicit dependencies stated — "redeem shares" implies shares exist → FR about minting?

Gap: referenced item missing, or implicit dependency unstated.

## 12. Internal Completeness

Criterion: every concept mentioned is defined somewhere.

Check: entity, role, state mentioned but no requirement about it.

Gap: concept used but never defined.

## 13. Redundancy

Criterion: no items express the same requirement differently, no item is strict subset of another.

Gap: duplicate or subset items → merge.

## 14. Triviality

Criterion: every item adds new testable information.

Gap: platform guarantee, tautology, or obvious consequence stated as requirement.
