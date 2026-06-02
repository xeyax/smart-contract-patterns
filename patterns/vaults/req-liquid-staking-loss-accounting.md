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

## R4: Pending Exits Are Not Harvestable Yield

**Amounts reserved for unstake or exit requests must be excluded from harvestable yield and free strategy liquidity.**

### What This Means

- Aggregate pending unstake amount and count are tracked.
- Yield calculations subtract pending exit obligations before reporting surplus.
- Failed push payments convert to user-specific pull claims rather than becoming yield.
- Queue settlement is bounded and preserves FIFO or documented ordering.
- Exit requests that use a cooldown should either fix the claim entitlement or bind the claim basis to a historical exchange rate so post-maturity claim timing cannot harvest later rewards.
- Pending staking exits should remain exposed to validator losses until the protocol-defined finalization point, not become harvestable yield or risk-free claims merely because the user entered a queue.

## R5: Burn-Cover Buckets Are Separate From Ordinary Rewards

**Cover burns, non-cover burns, fees, and positive rebases must be ordered explicitly so loss coverage cannot be mistaken for distributable profit.**

### What This Means

- Cover and non-cover burn requests are tracked separately.
- Positive rebase limits can defer burn-cover processing; cover is not always immediate repayment.
- Fees are not charged on non-profitable or loss-covering reports unless explicitly documented.

## Verification Checklist

| Requirement | Question |
|-------------|----------|
| R1 | Is slashing represented in on-chain state? |
| R2 | Can rewards be distributed before old penalties are repaid? |
| R3 | Do exits and migrations apply outstanding loss fairly? |
| R4 | Are pending exits excluded from yield and free liquidity? |
| R5 | Are cover burns, non-cover burns, and profit fees ordered explicitly? |

## Source Evidence

- StakeWise V2 tracks `totalPenalty`, repays penalties from later rewards before distribution, and applies outstanding penalty during migration.
- Lista's stkBNB strategy aggregates unstake requests, distributes in bounded FIFO batches, converts failed pushes to manual claims, and excludes pending unstake amounts from harvestable yield.
- BENQI sAVAX escrows shares for cooldown exits and claims against a historical rate lookup at the claimable timestamp in `/private/tmp/defillama-source/benqi-fi__BENQI-Smart-Contracts/sAVAX/StakedAvax.sol`, with pause liveness remaining a separate risk.
- Lido separates cover and non-cover share-burn requests, caps positive rebases, and avoids fees on non-profitable reports in `/private/tmp/defillama-source/lidofinance__core/contracts/0.8.9`.
- StakeWise V3 keeps exit-queue accounting in vault state and finalizes exits through oracle-reported vault data in `/private/tmp/defillama-source/stakewise__v3-core/contracts/vaults/modules/VaultState.sol`, `/private/tmp/defillama-source/stakewise__v3-core/contracts/vaults/modules/VaultEnterExit.sol`, and `/private/tmp/defillama-source/stakewise__v3-core/contracts/keeper/KeeperRewards.sol`.
- Puffer withdrawal requests remain dependent on protocol accounting and finalization in `/private/tmp/defillama-source/PufferFinance__puffer-contracts/mainnet-contracts/src/PufferWithdrawalManager.sol` and `/private/tmp/defillama-source/PufferFinance__puffer-contracts/mainnet-contracts/src/PufferProtocol.sol`.

## Related Patterns

- [Principal-Reward Split Derivative](../tokens/pattern-principal-reward-split-derivative.md)
- [Credit Loss Accounting Requirements](../lending/req-credit-loss-accounting.md)
- [Restaking Slashing Accounting Requirements](./req-restaking-slashing-accounting.md)
- [Rebasing Token Accounting](../../ANTIPATTERNS.md#rebasing-token-accounting)
