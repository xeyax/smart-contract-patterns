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

## Key Points

- Accrue rewards before changing position liquidity or boost state.
- Reuse the AMM's tick-crossing semantics where possible.
- Bound boost multipliers and reward emission rates.
- Define behavior for out-of-range positions clearly.
- Test range entry/exit, overlapping positions, boost changes, and emission updates.

## Source Evidence

- PancakeSwap V3 liquidity mining tracks reward growth through tick-level state so positions earn only while their concentrated-liquidity range is active.

## Related Patterns

- [Lazy Reward Index](./pattern-lazy-reward-index.md)
- [Range Fee-Growth Snapshots](../liquidity/pattern-range-fee-growth-snapshots.md)
