# Constant Product AMM Invariants

> Requirements for two-asset AMMs that maintain reserves, LP supply, protocol fees, and price accumulators around a constant-product invariant.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, constant-product, invariant, reserve, oracle |
| Type | Requirement |

## R1: Reserve State Matches Accounted Balances

**Reserves must be updated from observed balances only at defined synchronization points.**

### What This Means

- Swap, mint, burn, skim, and sync paths define when reserves change.
- Invariant checks use previous reserves and current balances consistently.
- Tests cover donations, direct transfers, skim, and sync behavior.

## R2: Fee-Adjusted Product Does Not Decrease

**After a swap, the fee-adjusted post-swap balances must preserve or increase `reserve0 * reserve1`.**

### What This Means

- Input amounts are inferred from deltas against previous reserves.
- Fees are applied before comparing the product.
- Zero-input and zero-output swaps are rejected.

## R3: LP Supply Has First-Deposit And Protocol-Fee Rules

**Initial liquidity, later mint/burn math, and protocol-fee minting must be deterministic and conservative.**

### What This Means

- First mint locks a minimum LP amount or uses another first-depositor defense.
- Later minting uses the smaller proportional contribution.
- Protocol fees are minted from documented invariant growth, such as `sqrt(k)`.

## R4: Oracle Accumulators Advance From Prior Reserves

**Cumulative price state must advance using the prior reserve ratio over elapsed time, not the just-mutated balance.**

### What This Means

- Price accumulators update before reserves are overwritten.
- Same-block swaps do not create artificial elapsed time.
- Timestamp overflow behavior is intentional and tested where compact timestamps are used.

## Verification Checklist

| Requirement | Question |
|-------------|----------|
| R1 | Are direct transfers, skim, and sync tested against reserve accounting? |
| R2 | Can any swap reduce the fee-adjusted product after rounding? |
| R3 | Are first liquidity, dust, burn-all, and protocol-fee cases covered? |
| R4 | Do price accumulators use elapsed time and previous reserves? |

## Source Evidence

- Uniswap V2 tests cover reserve updates, invariant preservation, first-liquidity locking, protocol-fee minting from `sqrt(k)` growth, and cumulative price updates.

## Related Patterns

- [Constant-Product Reserve-Delta AMM](./pattern-constant-product-reserve-delta-amm.md)
- [Minimum Liquidity Lock](./pattern-minimum-liquidity-lock.md)
- [TWAP Oracle](../oracles/pattern-twap-oracle.md)
