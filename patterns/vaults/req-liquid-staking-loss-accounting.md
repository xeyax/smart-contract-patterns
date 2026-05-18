# Liquid Staking Loss Accounting Requirements

> Requirements for liquid staking systems that must account for slashing, penalties, negative rewards, and migration under loss.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | liquid-staking, slashing, rewards, loss, migration |
| Type | Requirement |

## R1: Negative Rewards Are Explicit

**Slashing and validator penalties must accumulate in explicit loss or penalty state instead of being hidden in future reward math.**

### What This Means

- Negative rewards update a tracked penalty bucket.
- Reported rewards distinguish gross rewards, fees, and penalties.
- Tests cover zero, positive, and negative report periods.

## R2: Later Rewards Repay Outstanding Penalties First

**New rewards should not be distributed as profit while prior penalties remain unpaid unless that subsidy is documented.**

### What This Means

- Positive rewards reduce outstanding penalty before increasing claimable rewards.
- Fee calculation is ordered after penalty repayment.
- Rounding around partial repayment is explicit.

## R3: Migration And Exit Apply Remaining Losses Pro Rata

**Users leaving or migrating during an outstanding penalty period must carry their share of unrecovered loss.**

### What This Means

- Migration burns or conversion rates include outstanding penalties.
- Existing holders cannot dump unrecovered loss on remaining holders.
- Tests cover migration with full, partial, and no penalty repayment.

## Verification Checklist

| Requirement | Question |
|-------------|----------|
| R1 | Is slashing represented in on-chain state? |
| R2 | Can rewards be distributed before old penalties are repaid? |
| R3 | Do exits and migrations apply outstanding loss fairly? |

## Source Evidence

- StakeWise V2 tracks `totalPenalty`, repays penalties from later rewards before distribution, and applies outstanding penalty during migration.

## Related Patterns

- [Principal-Reward Split Derivative](../tokens/pattern-principal-reward-split-derivative.md)
- [Credit Loss Accounting Requirements](../lending/req-credit-loss-accounting.md)
- [Rebasing Token Accounting](../../ANTIPATTERNS.md#rebasing-token-accounting)
