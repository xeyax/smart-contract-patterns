# Amplified Stable Invariant

> Use an amplification parameter to make swaps near a peg behave like a high-liquidity constant-sum market while preserving constant-product style safety away from the peg.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, stable-swap, invariant, amplification, curve |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Assets should trade close to a shared value, peg, or redemption ratio
- Capital efficiency near balance matters more than supporting arbitrary volatile pairs
- The invariant can be implemented with bounded iterative math
- Governance can safely bound amplification changes

## Avoid When

- Assets can diverge significantly and permanently
- The pool cannot tolerate iterative invariant complexity
- Amplification can be changed instantly or without bounds

## Trade-offs

**Pros:**
- Far higher capital efficiency near the peg than constant-product, giving lower slippage per unit of liquidity for like-valued assets.
- Retains constant-product-style steepening when one asset is depleted, so the pool cannot be fully drained at near-flat prices.
- Amplification is tunable (with ramps) as confidence in the peg changes, without redeploying the pool.
- Mature reference implementations and test suites (Curve lineage) exist for convergence, ramping, and donation resistance.

**Cons:**
- Iterative Newton solvers for `D` and `y` cost materially more gas than closed-form invariants and must bound iterations and revert on non-convergence.
- Rounding direction inside the solver is subtle; small errors compound into LP-value leaks, so virtual-price monotonicity must be separately enforced.
- High amplification amplifies losses if the peg breaks — the flat region keeps quoting near-par prices while arbitrageurs drain the pool of the good asset.
- A-ramping is its own attack surface: unbounded or instant changes shift the invariant against LPs, so ramp speed and bounds need governance discipline.
- Rate-oracle, ERC4626, and fee-on-transfer extensions each add scaling layers that must feed actual received amounts into the invariant or accounting drifts.

## How It Works

Stable-swap pools compute an invariant `D` from balances and amplification `A`, then solve for output balance `y` after an input amount. The invariant is designed so the curve is flatter near equal balances and steeper when one asset is depleted.

```text
D = stable_invariant(balances, A)
y = solve_output_balance(D, balances_after_input, A)
amountOut = oldBalanceOut - y - fee
```

The iterative solver must have convergence bounds and explicit rounding direction.

Modern stable-swap variants may also use rate oracles, ERC4626 assets, and
stored balances. Those extensions do not change the core requirement: invariant
solvers, amplification ramps, and rate scaling must remain bounded and tested
across imbalanced states.

Simulation repositories are useful for parameter research, but should be
labeled as simulation evidence unless deployed code or tests confirm the exact
invariant and ramp behavior.

## Key Points

- Bound amplification and ramp speed.
- Test invariant convergence across balanced, imbalanced, dust, and max-balance states.
- Bound Newton iteration count and fail if the invariant does not converge.
- Apply slippage bounds to user-facing swaps and liquidity operations.
- Monitor off-peg balances because amplification increases loss if assets are not actually substitutable.
- Pair with virtual-price monotonicity requirements for LP accounting.
- When the stable basket supports fee-on-transfer collateral, compute invariant inputs from the actual received amount rather than the requested transfer amount.

## Source Evidence

- Curve StableSwap templates compute `D` and `y` through bounded iterative invariant math, model the same equations in tests, and use property-style exchange checks.
- Curve StableSwap NG computes bounded `D` and `y` values, supports A ramping,
  and tests donation resistance and A ramps in [`contracts/main/CurveStableSwapNG.vy:568-684`](https://github.com/curvefi/stableswap-ng/blob/2abe778f40206a6c0fd108a0a53ad3266cbedeee/contracts/main/CurveStableSwapNG.vy#L568-L684),
  [`contracts/main/CurveStableSwapNG.vy:760-870`](https://github.com/curvefi/stableswap-ng/blob/2abe778f40206a6c0fd108a0a53ad3266cbedeee/contracts/main/CurveStableSwapNG.vy#L760-L870),
  [`tests/pools/general/test_donation_get_D.py:7-30`](https://github.com/curvefi/stableswap-ng/blob/2abe778f40206a6c0fd108a0a53ad3266cbedeee/tests/pools/general/test_donation_get_D.py#L7-L30),
  and [`tests/pools/general/test_ramp_A.py:6-90`](https://github.com/curvefi/stableswap-ng/blob/2abe778f40206a6c0fd108a0a53ad3266cbedeee/tests/pools/general/test_ramp_A.py#L6-L90).
- mStable Masset uses StableSwap-style invariant validation for mint, swap, and redemption paths, applies slippage checks, supports A ramping, and measures transfer-fee assets before invariant accounting in [`contracts/masset/MassetLogic.sol`](https://github.com/mstable/mStable-contracts/blob/51da0272104d207abcbecb5dd545fec2e6abbfe9/contracts/masset/MassetLogic.sol) and [`contracts/masset/versions/MV2.sol`](https://github.com/mstable/mStable-contracts/blob/51da0272104d207abcbecb5dd545fec2e6abbfe9/contracts/masset/versions/MV2.sol).
- Yield Basis simulation material under [`btcusd`](https://github.com/yield-basis/yb-simulations/blob/e22d13db7b4d5c74266b46f40168829615e479b6/btcusd) explores stableswap invariant parameters, amplification, price-scale behavior, and dynamic fee variants; treat it as simulation-only evidence rather than deployed invariant proof.

## Related Patterns

- [Invariant-Delta Liquidity Accounting](./pattern-invariant-delta-liquidity-accounting.md)
- [LP Virtual Price Monotonicity Requirements](./req-lp-virtual-price-monotonicity.md)
- [Off-Peg Dynamic Fee](./pattern-offpeg-dynamic-fee.md)
