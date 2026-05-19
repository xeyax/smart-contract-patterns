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
- Virtual price should derive from stored/internal balances, not raw balances
  that a third party can increase through donation.
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

## R4: Transient Borrowed Reserves Are Accounted Consistently

**LP mint and burn math must include or exclude flash-borrowed reserves consistently across both sides of a transaction.**

### What This Means

- Flash-borrowed reserves do not make the pool appear undercollateralized during liquidity operations.
- Add and remove liquidity snapshots use the same reserve basis while a paired flash loan is open.
- Repayment checks clear the transient borrowed amount before the transaction ends.

## Source Evidence

- Curve defines LP virtual price as invariant value per total supply and includes stateful tests that virtual price does not decrease across swaps, liquidity operations, and amplification ramps.
- Curve StableSwap NG computes virtual price from invariant value and stored
  balances and tests monotonicity plus donation resistance in `/private/tmp/defillama-source/curvefi__stableswap-ng/contracts/main/CurveStableSwapNG.vy:1737-1755`,
  `/private/tmp/defillama-source/curvefi__stableswap-ng/tests/pools/general/test_virtual_price.py:8-84`,
  and `/private/tmp/defillama-source/curvefi__stableswap-ng/tests/pools/general/test_donation_get_D.py:7-30`.
- Sanctum's unstake pool includes flash-borrowed reserve amounts in pool-value snapshots for add/remove liquidity and resets them through paired borrow/repay instructions in `/private/tmp/defillama-source/igneous-labs_sanctum-unstake-program/programs/unstake/src/utils.rs`, `instructions/add_liquidity.rs`, `instructions/remove_liquidity.rs`, `instructions/take_flash_loan.rs`, and `instructions/repay_flash_loan.rs`.

## Related Patterns

- [Invariant-Delta Liquidity Accounting](./pattern-invariant-delta-liquidity-accounting.md)
- [Exchange-Rate Valuation Risk](../oracles/risk-exchange-rate-valuation.md)
- [Instruction-Paired Rebalance Solvency Record](./pattern-instruction-paired-rebalance-solvency-record.md)
