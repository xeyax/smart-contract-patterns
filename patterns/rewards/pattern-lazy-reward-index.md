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

## Trade-offs

**Pros:**
- O(1) accrual work per interaction regardless of user count; reward events never loop over users.
- Battle-tested shape across major protocols, so reviewers and integrators know what to expect.
- Checkpoint-on-interaction amortizes reward gas into operations users already perform.
- Extends naturally to multi-token rewards, emission schedules, and pluggable transfer strategies.

**Cons:**
- Every balance-changing path (mint, burn, transfer, liquidation, external ledger deltas) must checkpoint first; one missed hook misallocates rewards.
- Zero-supply intervals, token donations, and precision-scalar choices are recurring bug classes that need explicit handling.
- Zero-balance users must have their index cursor advanced, or later stake backfills rewards from before they entered.
- Reading pool supply from a shared token balance enables duplicate-pool double counting unless registration is constrained.
- The accumulated edge cases (schedules, terminal cursors, multi-token lists, external funding) make the test and audit surface large for such simple core math.

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
- Separate accrual math from transfer strategy. The reward index can compute
  user entitlement while pluggable transfer strategies decide whether rewards
  are pulled, staked, or routed elsewhere.
- Enforce one active pool per staking token when pool supply is derived from `stakingToken.balanceOf(farm)`, or track per-pool principal internally.
- When LP fees are removed from AMM reserves and claimed separately, hook LP balance changes so per-user fee indexes stay current across transfers.
- If rewards are funded by calling an external fee-claiming program, whitelist the external program and account index set, then account funding from the reward-vault balance delta.
- Piecewise reward-rate schedules should be sorted, bounded in size, checkpoint global rewards before mutation, and integrate cumulative emissions over every crossed segment.
- Option or liquidity-mining pools can derive allocation points from both governance votes and utilization, but must checkpoint pool reward indexes before changing utilization-derived weights.

## Source Evidence

- Aave V3 rewards accrue incentives through asset-level indexes and update users lazily when balances change or rewards are claimed.
- StakeWise V2 audit material highlights the need to checkpoint zero-balance users so later stake does not claim rewards from before the user entered.
- Dolomite's leveraged pot pool updates reward indexes before router-driven stake changes and liquidation balance deltas in an external margin ledger.
- Girin/Doppler-style reward distributors show terminal emission cursors that cap accrual at a final block and need guarded cutoff changes.
- Reserve staking audit material highlights precision-scalar and zero-supply accrual hazards in multi-reward lazy indexes.
- Satoshi Farm computes reward-per-token lazily over the interval clamped by reward start and end timestamps in [`src/core/Farm.sol`](https://github.com/Satoshi-Protocol/satoshi-farm/blob/174d930eb3c220fa3163a677cea019fc1550074e/src/core/Farm.sol) and `src/core/libraries/FarmMath.sol`.
- Zest Protocol incentives use reward-program cumulative indexes and per-user cursors before claim and vault routing in [`onchain/contracts/borrow/production/rewards/incentives.clar`](https://github.com/Zest-Protocol/zest-contracts/blob/3564bc38906e464ec4de774122bb9bbaee20ddc6/onchain/contracts/borrow/production/rewards/incentives.clar).
- Pendle V2 uses multi-token lazy reward indexes based on token balance deltas and per-user cursors in [`contracts/core/RewardManager`](https://github.com/pendle-finance/pendle-core-v2-public/blob/fdcfe39ed7b45717f0e6e286581bdcf96bb2f9ce/contracts/core/RewardManager).
- VVS Farm illustrates why duplicate staking-token registration must be blocked when MasterChef-style rewards use the farm's aggregate LP-token balance as pool supply in [`contracts/Craftsman.sol`](https://github.com/vvs-finance/vvs-farm/blob/acd79b99d88157b9d520eeac92e8c6424ae9d8de/contracts/Craftsman.sol).
- Velodrome V2 separates AMM fees into `PoolFees` and updates LP fee indexes on balance changes in [`contracts/Pool.sol`](https://github.com/velodrome-finance/contracts/blob/b3065d8b6702b14b094f9f6046b752cc9f78c43b/contracts/Pool.sol).
- Meteora Dynamic Fee Sharing funds reward vaults by whitelisted fee-claim CPI and reward-vault balance deltas in [`programs/dynamic-fee-sharing/src/instructions/ix_fund_by_claiming_fee.rs`](https://github.com/MeteoraAg/dynamic-fee-sharing/blob/f9be4a9a94cf21f1955344bd459eb120e0c8d5af/programs/dynamic-fee-sharing/src/instructions/ix_fund_by_claiming_fee.rs).
- Flare FAssets CollateralPool tracks per-account and global FAsset fee debt so entrants cannot claim historical fees and early withdrawals convert free fees into debt in [`contracts/collateralPool/implementation/CollateralPool.sol`](https://github.com/flare-foundation/fassets/blob/37c1be508a33c0d0ce31216aef45958fd4e5281e/contracts/collateralPool/implementation/CollateralPool.sol).
- Kamino Farms stores piecewise reward-rate schedules, checkpoints reward state before schedule changes, and integrates cumulative emissions over crossed segments in [`programs/kfarms/src/state.rs`](https://github.com/Kamino-Finance/kfarms/blob/2a63e5ab59629c77f8b4043781c1e4b4572c7b60/programs/kfarms/src/state.rs) and `programs/kfarms/src/farm_operations.rs`.
- Aave V3 periphery separates reward accrual in `RewardsDistributor` from
  transfer strategies used by `RewardsController` in [`contracts/rewards/RewardsDistributor.sol:284`](https://github.com/aave/aave-v3-periphery/blob/8bb2493678bbb31532249f1e488fffe5f53a2d1a/contracts/rewards/RewardsDistributor.sol#L284),
  [`contracts/rewards/RewardsController.sol:214`](https://github.com/aave/aave-v3-periphery/blob/8bb2493678bbb31532249f1e488fffe5f53a2d1a/contracts/rewards/RewardsController.sol#L214),
  and [`contracts/rewards/transfer-strategies/TransferStrategyBase.sol:23`](https://github.com/aave/aave-v3-periphery/blob/8bb2493678bbb31532249f1e488fffe5f53a2d1a/contracts/rewards/transfer-strategies/TransferStrategyBase.sol#L23).
- Premia Mining accrues pool rewards with `accPremiaPerShare`, caps emissions by available rewards, and updates allocation points from votes and utilization in [`contracts/mining/PremiaMining.sol`](https://github.com/premiafinance/premia-contracts/blob/0ed54a91c6b69b17a8cc9d6208aadb442218a07f/contracts/mining/PremiaMining.sol).

## Related Patterns

- [Queued Reward Streaming](./pattern-queued-reward-streaming.md)
- [Lazy Borrow Index](../lending/pattern-lazy-borrow-index.md)
- [Index-To-Distributor Reward Routing](./pattern-index-to-distributor-reward-routing.md)
- [Reward Token Accrual DoS](./risk-reward-token-accrual-dos.md)
- [Segregated AMM Fee Escrow](../liquidity/pattern-segregated-amm-fee-escrow.md)
