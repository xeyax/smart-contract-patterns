# Lazy Reward Index

> Accrue rewards through a global index and update each user only when they interact or claim.

## Metadata

| Property | Value |
|----------|-------|
| Category | rewards |
| Tags | rewards, index, lazy-accounting, staking, incentives |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- Rewards accrue continuously or per emission update
- The protocol has many suppliers, stakers, or borrowers
- Updating every user on every reward event is impossible
- User rewards are needed only on interaction or claim

## Avoid When

- Rewards are one-off Merkle claims
- Per-user boosts require expensive global recomputation
- Reward tokens can be donated and mistakenly counted as newly accrued rewards
- The same staking asset can be registered in multiple pools while pool supply is read from a shared token balance

## How It Works

Track cumulative reward per unit of stake:

```solidity
function updateGlobalIndex(uint256 rewardAccrued) internal {
    if (totalStake == 0) return;
    rewardIndex += rewardAccrued * 1e18 / totalStake;
}

function updateUser(address user) internal {
    uint256 delta = rewardIndex - userIndex[user];
    accrued[user] += balance[user] * delta / 1e18;
    userIndex[user] = rewardIndex;
}
```

Call `updateUser` before changing the user's stake and before claiming.

## Key Points

- Update the global index before changing total stake if new rewards are available.
- Update the user index before mint, burn, transfer, borrow, repay, or claim changes their earning base.
- If the earning base lives in an external lending or margin ledger, checkpoint indexes inside authorized callbacks before applying liquidation or delegated balance deltas.
- Define behavior when total stake is zero.
- Keep reward-token balance accounting separate from emitted reward accounting.
- Use an explicit high-precision scalar independent of reward token decimals, and carry forward or recover rewards that accrue while total stake is zero.
- If a user has zero earning balance, advance their user index cursor to the latest index so future stake cannot backfill historical rewards.
- A proportional reward pool can use virtual fee debt instead of a cumulative index: new entrants receive debt equal to their pro-rata historical-fee entitlement, and early fee withdrawals convert free fees into per-account debt.
- Terminal emission cursors should cap accrual at the configured final block or timestamp; setters must reject past cutoffs and avoid silently extending an expired distributor.
- Reward-per-token math should clamp accrual to the configured emission start/end window before dividing by total stake.
- For multi-token reward lists, treat reward-token registration and balance-delta reads as a liveness boundary for transfers and exits.
- Test multiple users entering, exiting, and claiming across emission updates.
- Enforce one active pool per staking token when pool supply is derived from `stakingToken.balanceOf(farm)`, or track per-pool principal internally.
- When LP fees are removed from AMM reserves and claimed separately, hook LP balance changes so per-user fee indexes stay current across transfers.
- If rewards are funded by calling an external fee-claiming program, whitelist the external program and account index set, then account funding from the reward-vault balance delta.

## Source Evidence

- Aave V3 rewards accrue incentives through asset-level indexes and update users lazily when balances change or rewards are claimed.
- StakeWise V2 audit material highlights the need to checkpoint zero-balance users so later stake does not claim rewards from before the user entered.
- Dolomite's leveraged pot pool updates reward indexes before router-driven stake changes and liquidation balance deltas in an external margin ledger.
- Girin/Doppler-style reward distributors show terminal emission cursors that cap accrual at a final block and need guarded cutoff changes.
- Reserve staking audit material highlights precision-scalar and zero-supply accrual hazards in multi-reward lazy indexes.
- Satoshi Farm computes reward-per-token lazily over the interval clamped by reward start and end timestamps in `/private/tmp/defillama-source/Satoshi-Protocol__satoshi-farm/src/core/Farm.sol` and `src/core/libraries/FarmMath.sol`.
- Zest Protocol incentives use reward-program cumulative indexes and per-user cursors before claim and vault routing in `/private/tmp/defillama-source/Zest-Protocol__zest-contracts/onchain/contracts/borrow/production/rewards/incentives.clar`.
- Pendle V2 uses multi-token lazy reward indexes based on token balance deltas and per-user cursors in `/private/tmp/defillama-source/pendle-finance__pendle-core-v2-public/contracts/core/RewardManager`.
- VVS Farm illustrates why duplicate staking-token registration must be blocked when MasterChef-style rewards use the farm's aggregate LP-token balance as pool supply in `/private/tmp/defillama-source/vvs-finance__vvs-farm/contracts/Craftsman.sol`.
- Velodrome V2 separates AMM fees into `PoolFees` and updates LP fee indexes on balance changes in `/private/tmp/defillama-source/velodrome-finance__contracts/contracts/Pool.sol`.
- Meteora Dynamic Fee Sharing funds reward vaults by whitelisted fee-claim CPI and reward-vault balance deltas in `/private/tmp/defillama-source/MeteoraAg_dynamic-fee-sharing/programs/dynamic-fee-sharing/src/instructions/ix_fund_by_claiming_fee.rs`.
- Flare FAssets CollateralPool tracks per-account and global FAsset fee debt so entrants cannot claim historical fees and early withdrawals convert free fees into debt in `/private/tmp/defillama-source/flare-foundation_fassets/contracts/collateralPool/implementation/CollateralPool.sol`.

## Related Patterns

- [Queued Reward Streaming](./pattern-queued-reward-streaming.md)
- [Lazy Borrow Index](../lending/pattern-lazy-borrow-index.md)
- [Index-To-Distributor Reward Routing](./pattern-index-to-distributor-reward-routing.md)
- [Reward Token Accrual DoS](./risk-reward-token-accrual-dos.md)
- [Segregated AMM Fee Escrow](../liquidity/pattern-segregated-amm-fee-escrow.md)
