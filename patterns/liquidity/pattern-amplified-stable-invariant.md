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

## Key Points

- Bound amplification and ramp speed.
- Test invariant convergence across balanced, imbalanced, dust, and max-balance states.
- Bound Newton iteration count and fail if the invariant does not converge.
- Apply slippage bounds to user-facing swaps and liquidity operations.
- Monitor off-peg balances because amplification increases loss if assets are not actually substitutable.
- Pair with virtual-price monotonicity requirements for LP accounting.

## Source Evidence

- Curve StableSwap templates compute `D` and `y` through bounded iterative invariant math, model the same equations in tests, and use property-style exchange checks.
- Curve StableSwap NG computes bounded `D` and `y` values, supports A ramping,
  and tests donation resistance and A ramps in `/private/tmp/defillama-source/curvefi__stableswap-ng/contracts/main/CurveStableSwapNG.vy:568-684`,
  `/private/tmp/defillama-source/curvefi__stableswap-ng/contracts/main/CurveStableSwapNG.vy:760-870`,
  `/private/tmp/defillama-source/curvefi__stableswap-ng/tests/pools/general/test_donation_get_D.py:7-30`,
  and `/private/tmp/defillama-source/curvefi__stableswap-ng/tests/pools/general/test_ramp_A.py:6-90`.

## Related Patterns

- [Invariant-Delta Liquidity Accounting](./pattern-invariant-delta-liquidity-accounting.md)
- [LP Virtual Price Monotonicity Requirements](./req-lp-virtual-price-monotonicity.md)
- [Off-Peg Dynamic Fee](./pattern-offpeg-dynamic-fee.md)
