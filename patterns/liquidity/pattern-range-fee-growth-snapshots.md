# Range Fee-Growth Snapshots

> Track fee growth outside and inside each tick range so concentrated-liquidity positions can accrue fees lazily without iterating over LPs.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, fee, concentrated-liquidity, ticks, lazy-accounting |
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

## Trade-offs

**Pros:**
- Swap-time fee accounting is O(ticks crossed), independent of position count, so pools scale to thousands of LPs.
- Fees accrue lazily; positions pay update costs only on mint, burn, or collect rather than on every swap.
- Per-range accrual pays fees only while a position is in range, matching LP risk to LP reward exactly.
- Separating fee collection from liquidity removal lets LPs harvest without touching their range.

**Cons:**
- Inside/outside subtraction semantics rely on intentional accumulator overflow; the math is unintuitive and wrong-by-one tick handling silently misallocates fees.
- Every tick crossing must flip outside growth; a missed or double flip corrupts fee accounting for all positions sharing that tick.
- Position fees are stale until an owner-triggered snapshot, so external readers must replicate the inside-growth math to value positions accurately.
- Tick state storage and crossing updates add gas to swaps that traverse many initialized ticks.
- Correctness depends on a wide test matrix — overlapping ranges, repeated crossings, zero-liquidity ticks, partial collects — that is expensive to build and maintain.

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
- Orca Whirlpools stores tick fee and reward growth outside in [`programs/whirlpool/src/state/tick.rs`](https://github.com/orca-so/whirlpools/blob/a119d79bada4e730fef791cac6adb669405a21de/programs/whirlpool/src/state/tick.rs), flips outside growth in `manager/tick_manager.rs`, and updates ticks, global liquidity, and fee/reward growth in `manager/liquidity_manager.rs`.

## Related Patterns

- [Concentrated Liquidity Ranges](./pattern-concentrated-liquidity-ranges.md)
- [Lazy Reward Index](../rewards/pattern-lazy-reward-index.md)
