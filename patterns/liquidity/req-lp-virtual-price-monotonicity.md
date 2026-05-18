# LP Virtual Price Monotonicity Requirements

> Requirements for AMM LP tokens whose fair value is represented by invariant value per LP share.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, lp-token, virtual-price, invariant, monotonicity |
| Type | Requirement |

## R1: Fee-Only Operations Do Not Decrease Virtual Price

**Swaps and fee-generating liquidity operations should not reduce invariant value per LP share except through explicit losses or admin withdrawals.**

### What This Means

- `virtualPrice = invariant / totalSupply` should be non-decreasing across ordinary swaps.
- Fees should accrue to LPs, not disappear through rounding.
- Tests should cover swap, deposit, withdrawal, and parameter-ramp sequences.

## R2: Share Supply Changes Match Invariant Delta

**LP mint and burn amounts must correspond to the fee-adjusted invariant delta.**

### What This Means

- New LPs do not receive existing accrued value for free.
- Exiting LPs cannot burn fewer shares than the invariant value they remove.
- Rounding is explicitly biased and bounded.

## R3: Cached Virtual Prices Preserve Freshness Semantics

**If a pool caches another LP token's virtual price, the cache age and update path must be explicit.**

### What This Means

- Metapools do not silently treat stale base-pool virtual prices as current.
- Read-only and write-updating paths are clearly separated.
- Integrators know whether virtual price is fair-value accounting or a market price.

## Source Evidence

- Curve defines LP virtual price as invariant value per total supply and includes stateful tests that virtual price does not decrease across swaps, liquidity operations, and amplification ramps.

## Related Patterns

- [Invariant-Delta Liquidity Accounting](./pattern-invariant-delta-liquidity-accounting.md)
- [Exchange-Rate Valuation Risk](../oracles/risk-exchange-rate-valuation.md)
