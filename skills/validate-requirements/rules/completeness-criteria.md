# Completeness Criteria

Set-level checks. Used by proposer (to find what to generate) and validator (to find what's missing).

For each criterion: if gap found → proposer generates item, validator flags issue.

## 1. Purpose & Scope

Criterion: document has `## Purpose` section (what the system does) and `## Scope` section (in-scope / out-of-scope). These are document sections, not FR/NFR/C/R items.

Gap: no Purpose section or no Scope section.

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

Build a state × action matrix. Every "?" cell (undefined behavior for a state+action pair) = separate issue. Don't just show the matrix — flag each gap explicitly.

Gap: state exists but behavior for some functions undefined in that state.

## 6. NFR Category Coverage

Criterion: each relevant category addressed.

Categories: security, performance, compatibility, upgradeability, observability, reliability.

Gap: category clearly relevant but no NFR for it.

## 7. Risk ↔ FR Mapping

Criterion: every risk has a mitigation statement (WHAT-level constraint within the R item itself) or explicit "accepted" decision. A separate mitigating FR is NOT required — the mitigation in R IS the requirement. A separate FR is only expected if it adds new capability beyond the risk mitigation.

Gap: risk without mitigation and without "accepted" status.

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

## Context-Aware Validation

Before flagging a missing protection or risk:
1. **Check structural mitigation.** Do existing items already prevent this? Example: async deposit + keeper settlement + cooldown = same-block MEV is structurally impossible. Don't flag "missing MEV protection" when async flow already prevents it.
2. **Verify attacker controllability.** Does the attacker actually control the vector? Example: if emergency chunks are fixed-size (not caller-controlled), griefing via "minimum amount" is impossible. Don't flag DoS when the parameter isn't user-controlled.

Rule: read ALL existing items before flagging any gap. A gap is only real if no combination of existing items covers it.

## Severity Guide

Use ERROR (not WARNING) for gaps that are critical for the system type:

**For financial systems / vaults:**
- Rounding direction not specified → ERROR
- External dependency failure mode missing → ERROR
- Initialization/deployment requirements missing → ERROR
- Deposit/withdrawal MEV protection gap → ERROR

**For any system:**
- Contradictions between items → ERROR
- Risk without mitigation statement and without "accepted" status → ERROR
- Actor with no requirements → WARNING
- Missing NFR category → WARNING
- Undefined state×action pair → WARNING per cell
- Redundancy → WARNING
