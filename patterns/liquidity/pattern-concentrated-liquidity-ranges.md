# Concentrated Liquidity Ranges

> Represent LP positions as liquidity active only between lower and upper ticks so capital is concentrated around selected prices.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, concentrated-liquidity, ticks, ranges, lp |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- LPs should choose price ranges instead of passively providing across all prices
- Capital efficiency matters around expected trading ranges
- The AMM can maintain tick state, range accounting, and fee snapshots
- Users can tolerate active management or automation

## Avoid When

- A simple constant-product pool is sufficient
- Users cannot understand out-of-range inventory behavior
- Tick crossing and position accounting cannot be thoroughly tested

## How It Works

Each position specifies a lower tick, upper tick, and liquidity amount:

```solidity
struct Position {
    int24 tickLower;
    int24 tickUpper;
    uint128 liquidity;
}
```

If the current price is below the range, the position is entirely token0. If inside, it contributes active liquidity and holds both tokens. If above, it is entirely token1.

## Key Points

- Validate tick order, tick spacing, and max liquidity per tick.
- Update active liquidity only when the current price is inside the range.
- Snapshot fee growth when minting, burning, and collecting.
- Make swap price limits mandatory so swaps cannot cross arbitrary range state unexpectedly.
- Warn LPs that out-of-range positions stop earning fees until price re-enters the range.

## Source Evidence

- Uniswap V3 and PancakeSwap V3 tests cover minting below, inside, and above the current price and verify active liquidity changes when swaps enter and exit ranges.

## Related Patterns

- [Concentrated Liquidity Invariants](./req-concentrated-liquidity-invariants.md)
- [Range Fee-Growth Snapshots](./pattern-range-fee-growth-snapshots.md)
- [Canonical AMM Pool Factory](./pattern-canonical-amm-pool-factory.md)
