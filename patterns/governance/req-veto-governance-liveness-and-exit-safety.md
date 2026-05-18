# Veto Governance Liveness And Exit Safety Requirements

> Requirements for governance systems where stakeholder veto support can delay proposals and escalate into an exit process.

## Metadata

| Property | Value |
|----------|-------|
| Category | governance |
| Tags | governance, veto, liveness, exit, rage-quit |
| Type | Requirement |

## R1: Proposal Scheduling Remains Bounded

**Veto states must define exactly when proposals can be submitted, scheduled, executed, cancelled, or resubmitted.**

### What This Means

- Cooldowns do not block proposal flow forever.
- Post-veto proposal rules are explicit.
- Proposal ids or executors cannot bypass veto state.

## R2: Exit Escalation Has One Clear Active Cohort

**A rage-quit or settlement escalation must identify the participating cohort and prevent ambiguous overlapping exits.**

### What This Means

- The locked support set is snapshotted or frozen at activation.
- Later signaling uses a separate escrow or state bucket.
- Concurrent escalations are either impossible or deliberately modeled.

## R3: Exit Processing Is Public And Bounded

**No single keeper or unbounded loop should be required to finish stakeholder exits.**

### What This Means

- Anyone can process a limited batch.
- Claims use fixed entitlement or deterministic queue rules.
- Pauses and emergency controls preserve the safest solvent exit path.

## R4: Deadlock Recovery Is Objective

**If governance can wait on an external exit path, recovery rules need objective conditions, timeouts, and narrow powers.**

### What This Means

- Recovery cannot be invoked during normal disagreement.
- Tiebreaker actions are enumerated.
- Events and monitoring show why recovery became available.

## Source Evidence

- Lido Dual Governance documents state-dependent proposal scheduling, one active rage-quit path, bounded public exit processing, and tiebreaker recovery for prolonged blocked states.

## Related Patterns

- [Stakeholder-Extensible Governance Timelock](./pattern-stakeholder-extensible-governance-timelock.md)
- [Local Settlement Rage-Quit Escrow](./pattern-local-settlement-rage-quit-escrow.md)
- [Condition-Gated Deadlock Tiebreaker](./pattern-condition-gated-deadlock-tiebreaker.md)
