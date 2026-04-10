# Completeness Criteria

Set-level checks. Used by proposer (to find what to generate) and validator (to find what's missing).

For each criterion: if gap found → proposer generates item, validator flags issue.

## 1. Purpose

Criterion: document has `## Purpose` section (what the system does, for whom). This is a document section, not an FR/NFR/C/R item.

Out-of-scope items are captured as deferred items with "out of scope" reasoning — no separate Scope section needed.

Gap: no Purpose section.

## 2. Grouping & Order

Criterion: items grouped by domain/flow. Order: core → extensions → operations. Related items adjacent.

Gap: items randomly ordered, related items far apart → cognitive load.

## 3. Participant Coverage

Criterion: every participant category mentioned or implied has ≥1 item.

Participant categories (abstract, not specific role names):
- Depositors / users (unprivileged)
- Privileged roles (restricted operations — configuration, emergency, rebalance)
- Permissionless callers (if any operations are open to anyone)
- External dependencies (protocols, oracles)

Do NOT require specific role names (owner, keeper, operator, admin) — those are architecture decisions. Check that each category of participant has items, not specific roles.

Gap: participant category implied but no item describes their interaction.

## 4. Action Coverage

Criterion: for each participant category, all expected actions have items.

Common actions per participant category:
- Depositors/users: deposit, withdraw/redeem, claim
- Privileged roles: configure parameters, pause, emergency actions
- Permissionless: trigger time-sensitive operations, liquidations
- External: price updates, callbacks, protocol interactions

Gap: expected action for a participant category has no item.

## 5. State Coverage

Criterion: for each system state (normal, paused, emergency, uninitialized), ALL relevant behaviors defined.

For each state: what works? what's blocked? how to enter? how to exit?

Build a state × action matrix. Every "?" cell (undefined behavior for a state+action pair) = separate issue. Don't just show the matrix — flag each gap explicitly.

Gap: state exists but behavior for some functions undefined in that state.

## 6. NFR Category Coverage

Criterion: each relevant category addressed.

Categories: security, performance, compatibility, upgradeability, observability, reliability.

Gap: category clearly relevant but no NFR for it.

## 7. Risk Identification

Criterion: risks relevant to the system are identified. In requirements, R items are threat descriptions only — no mitigation, no "accepted" status. Architecture phase is responsible for addressing each risk.

At requirements level, check: are there obvious risks NOT listed? Missing risk for a known threat category → gap.

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

Note: Redundancy and triviality are per-item checks in quality-rules.md (rules 8-9), not set-level completeness criteria.

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
- Obvious risk not identified → WARNING
- Participant category with no requirements → WARNING
- Missing NFR category → WARNING
- Undefined state×action pair → WARNING per cell
- Redundancy → WARNING
