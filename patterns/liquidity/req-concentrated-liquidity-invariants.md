# Concentrated Liquidity Invariants

> Requirements for AMMs where active liquidity depends on the current tick and liquidity ranges rather than total deposited inventory.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, concentrated-liquidity, ticks, invariant, range |
| Type | Requirement |

## R1: Active Liquidity Matches Tick State

**The pool's active liquidity must equal the net liquidity implied by initialized ticks around the current price.**

### What This Means

- Total deposited liquidity is not the same as active swap liquidity.
- Crossing a lower or upper tick updates active liquidity with the correct sign.
- The sum of all `liquidityNet` changes should balance to zero.

## R2: Range Entry and Exit Are Atomic

**A swap crossing a tick must update price, tick, liquidity, fee growth, and observations consistently.**

### What This Means

- No intermediate state lets callbacks or reads observe mismatched tick/liquidity.
- Tick crossing handles zero-liquidity and boundary conditions explicitly.
- Swap loops are bounded by price limits and gas-aware tick spacing.

## R3: Position Accounting Uses Range Snapshots

**Fees and liquidity owed to a position are derived from inside-range growth snapshots, not global pool growth alone.**

### What This Means

- Position updates snapshot fee growth inside its lower/upper ticks.
- Collecting fees does not require iterating over other positions.
- Overflow behavior in fee-growth accumulators is intentional and tested.

## Source Evidence

- Uniswap V3 and PancakeSwap V3 derive active liquidity from initialized tick ranges, update liquidity on tick crossing, and use Echidna/property tests for liquidity-net and active-liquidity invariants.
- Orca Whirlpools bounds swap steps to the next initialized tick or price limit in `/private/tmp/defillama-source/orca-so__whirlpools/programs/whirlpool/src/manager/swap_manager.rs`, while tick crossing and liquidity updates maintain range accounting in `tick_manager.rs` and `liquidity_manager.rs`.

## Related Patterns

- [Concentrated Liquidity Ranges](./pattern-concentrated-liquidity-ranges.md)
- [Range Fee-Growth Snapshots](./pattern-range-fee-growth-snapshots.md)
- [Tick Crossing Gas DoS Risk](./risk-tick-crossing-gas-dos.md)
