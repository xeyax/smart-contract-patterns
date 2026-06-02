# Range Liquidity Reward Index

> Accrue rewards only to concentrated-liquidity positions whose tick ranges are active, using tick-level reward-growth snapshots.

## Metadata

| Property | Value |
|----------|-------|
| Category | rewards |
| Tags | rewards, concentrated-liquidity, index, ticks, farming |
| Complexity | High |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- Rewards should incentivize active AMM liquidity, not out-of-range inventory
- LP positions have lower and upper ticks
- Reward growth can be tracked at the same tick boundaries as fee growth
- Boosts or caps need to be applied per position or pool

## Avoid When

- All stakers should earn rewards regardless of range activity
- Tick crossing data is not available to the reward contract
- Reward accounting cannot stay synchronized with AMM liquidity changes

## How It Works

Maintain reward growth globally and outside ticks. A position earns from reward growth inside its range:

```solidity
rewardGrowthInside = rewardGrowthGlobal
    - rewardGrowthOutside(lower)
    - rewardGrowthOutside(upper);

rewardOwed += positionLiquidity * (rewardGrowthInside - rewardGrowthInsideLast) / Q128;
```

The reward pool updates tick state when the AMM crosses ticks or when position liquidity changes.

### Seconds-Per-Liquidity Snapshot Variant

If the AMM exposes `secondsPerLiquidityInside` snapshots for a range, an
external staking contract can checkpoint that accumulator at stake time and
unstake time. Rewards are proportional to liquidity multiplied by the increase
in seconds-per-liquidity inside the range, so only in-range time earns.

## Key Points

- Accrue rewards before changing position liquidity or boost state.
- Reuse the AMM's tick-crossing semantics where possible.
- Bound boost multipliers and reward emission rates.
- Define behavior for out-of-range positions clearly.
- Bound incentive creation with a start lead time and max duration, prevent
  ending while positions remain staked, allow public unstake after incentive end,
  and bind leftover reward recovery to the configured refund recipient.
- Test range entry/exit, overlapping positions, boost changes, and emission updates.

## Source Evidence

- PancakeSwap V3 liquidity mining tracks reward growth through tick-level state so positions earn only while their concentrated-liquidity range is active.
- Uniswap V3 Staker computes rewards from `snapshotCumulativesInside` and
  `RewardMath` seconds-per-liquidity deltas in `/private/tmp/defillama-source/Uniswap__v3-staker/contracts/UniswapV3Staker.sol:233`,
  `/private/tmp/defillama-source/Uniswap__v3-staker/contracts/libraries/RewardMath.sol:21`,
  and `/private/tmp/defillama-source/Uniswap__v3-staker/test/unit/Stakes.spec.ts:315`.
- Uniswap V3 Staker bounds incentive lifecycle with start/duration checks,
  no-end-while-staked behavior, post-end unstake, and refundee-bound leftover
  recovery in `/private/tmp/defillama-source/Uniswap__v3-staker/contracts/UniswapV3Staker.sol:96`,
  `/private/tmp/defillama-source/Uniswap__v3-staker/test/unit/Incentives.spec.ts:198`,
  and `/private/tmp/defillama-source/Uniswap__v3-staker/test/unit/Stakes.spec.ts:583`.

## Related Patterns

- [Lazy Reward Index](./pattern-lazy-reward-index.md)
- [Range Fee-Growth Snapshots](../liquidity/pattern-range-fee-growth-snapshots.md)
