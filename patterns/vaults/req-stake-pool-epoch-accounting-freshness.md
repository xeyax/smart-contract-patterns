# Stake Pool Epoch Accounting Freshness Requirements

> Requirements for Solana stake-pool and LST systems that value shares from delegated stake.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, solana, stake-pool, epoch, freshness |
| Type | Requirement |

## R1: Validator Records Are Current Before Value Changes

**Validator stake records must be updated for the current epoch before validator add/remove, rebalancing, or exchange-rate conversion.**

### What This Means

- Stale validator entries are rejected before pool totals are trusted.
- Validator-list length and pool epoch are checked before maintenance actions.
- Exchange-rate calculators fail closed when backing data is not current.

## R2: Pool Backing Is Recomputed From Validated Components

**Pool totals are recomputed from validated reserve stake plus per-validator delegated stake.**

### What This Means

- Reserve balances and validator stake entries are validated as a cohort.
- Direct rewards or lamport changes are absorbed only through the stake-pool accounting path.
- Pool token supply and total backing snapshots are updated together.

## R3: Prior-Epoch Snapshots Support Fees And Rewards

**Previous-epoch totals and supply are preserved for fee, reward, and maintenance accounting.**

### What This Means

- Fee and reward accounting can compare prior and current backing.
- Maintenance cranks have an explicit liveness dependency.
- Keepers or public cranks are monitored because stale freshness can stall value-changing flows.

## Source Evidence

- SPL Stake Pool rejects stale validator entries before recomputing pool backing, requires current pool epoch for validator add/remove, and tests reward absorption and wrong-account failures.
- Jito StakeNet and Sanctum calculators require current stake-pool freshness before epoch maintenance or LST/SOL conversion.

## Related Patterns

- [Operation Cadence Liveness Agent](../monitoring/pattern-operation-cadence-liveness-agent.md)
- [Operator-Routed Liquid Staking Share](./pattern-operator-routed-liquid-staking-share.md)
- [Exchange-Rate Valuation Risk](../oracles/risk-exchange-rate-valuation.md)
