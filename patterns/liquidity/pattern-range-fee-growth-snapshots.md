# Range Fee-Growth Snapshots

> Track fee growth outside and inside each tick range so concentrated-liquidity positions can accrue fees lazily without iterating over LPs.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, fees, concentrated-liquidity, ticks, lazy-accounting |
| Complexity | High |
| Gas Efficiency | High |
| Audit Risk | High |

## Use When

- LP positions are active only inside price ranges
- Fees should accrue only while a position's range is active
- The pool has many positions and cannot update them all on every swap
- Tick crossing state can snapshot outside fee growth

## Avoid When

- All LPs share one global pro-rata fee index
- Range ticks are not explicit state
- Overflow-tolerant accumulator math cannot be tested

## How It Works

Maintain global fee growth and per-tick fee growth outside:

```solidity
feeGrowthInside = feeGrowthGlobal
    - feeGrowthOutside(lower)
    - feeGrowthOutside(upper);

tokensOwed += liquidity * (feeGrowthInside - feeGrowthInsideLast) / Q128;
feeGrowthInsideLast = feeGrowthInside;
```

When the current price crosses a tick, the pool flips that tick's outside growth so future inside/outside calculations remain correct.

## Key Points

- Snapshot position fee growth when minting, burning, or collecting.
- Update tick outside growth when crossing ticks.
- Treat accumulator overflow as intentional only if subtraction semantics are tested.
- Keep fee collection separate from liquidity removal.
- Test multiple LP ranges, repeated crossing, zero-liquidity ticks, and partial collects.

## Source Evidence

- Uniswap V3 and PancakeSwap V3 store position fee-growth snapshots, update tick outside growth on crossing, and test fee splits across overlapping LP ranges.
- Orca Whirlpools stores tick fee and reward growth outside in `/private/tmp/defillama-source/orca-so__whirlpools/programs/whirlpool/src/state/tick.rs`, flips outside growth in `manager/tick_manager.rs`, and updates ticks, global liquidity, and fee/reward growth in `manager/liquidity_manager.rs`.

## Related Patterns

- [Concentrated Liquidity Ranges](./pattern-concentrated-liquidity-ranges.md)
- [Lazy Reward Index](../rewards/pattern-lazy-reward-index.md)
