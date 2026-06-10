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

## Trade-offs

**Pros:**
- Emissions pay only in-range liquidity, so incentives buy actual swap depth instead of idle inventory.
- O(1) accrual per position via tick snapshots — no iteration over stakers or positions.
- Reuses the AMM's tick-crossing and fee-growth semantics, keeping reward math consistent with fee math.
- Seconds-per-liquidity variant lets an external staker work without modifying the pool contract.

**Cons:**
- Tick-level reward state must stay synchronized with every liquidity change and tick crossing; one missed update misallocates rewards silently.
- `rewardGrowthOutside` initialization relative to the current tick is subtle and a recurring audit hotspot.
- Requires tick or snapshot data from the AMM — not portable to pools that do not expose it.
- Just-in-time liquidity concentrated around the current tick can capture an outsized share of emissions.
- Incentive lifecycle handling (start lead time, end-while-staked, refunds, post-end unstake) adds operational and test burden.

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
  `RewardMath` seconds-per-liquidity deltas in [`contracts/UniswapV3Staker.sol:233`](https://github.com/Uniswap/v3-staker/blob/6d06fe4034e4eec53e1e587fc4770286466f4b35/contracts/UniswapV3Staker.sol#L233),
  [`contracts/libraries/RewardMath.sol:21`](https://github.com/Uniswap/v3-staker/blob/6d06fe4034e4eec53e1e587fc4770286466f4b35/contracts/libraries/RewardMath.sol#L21),
  and [`test/unit/Stakes.spec.ts:315`](https://github.com/Uniswap/v3-staker/blob/6d06fe4034e4eec53e1e587fc4770286466f4b35/test/unit/Stakes.spec.ts#L315).
- Uniswap V3 Staker bounds incentive lifecycle with start/duration checks,
  no-end-while-staked behavior, post-end unstake, and refundee-bound leftover
  recovery in [`contracts/UniswapV3Staker.sol:96`](https://github.com/Uniswap/v3-staker/blob/6d06fe4034e4eec53e1e587fc4770286466f4b35/contracts/UniswapV3Staker.sol#L96),
  [`test/unit/Incentives.spec.ts:198`](https://github.com/Uniswap/v3-staker/blob/6d06fe4034e4eec53e1e587fc4770286466f4b35/test/unit/Incentives.spec.ts#L198),
  and [`test/unit/Stakes.spec.ts:583`](https://github.com/Uniswap/v3-staker/blob/6d06fe4034e4eec53e1e587fc4770286466f4b35/test/unit/Stakes.spec.ts#L583).

## Related Patterns

- [Lazy Reward Index](./pattern-lazy-reward-index.md)
- [Range Fee-Growth Snapshots](../liquidity/pattern-range-fee-growth-snapshots.md)
