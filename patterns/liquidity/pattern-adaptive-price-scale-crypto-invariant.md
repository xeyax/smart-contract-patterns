# Adaptive Price-Scale Crypto Invariant

> Maintain a crypto-asset AMM invariant while adjusting the internal price scale only after profit-gated evidence that the pool can absorb the move.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, crypto, invariant, price-scale, curve |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Assets are volatile but the AMM still wants concentrated liquidity around an
  internal price scale
- The pool can solve a non-stable invariant with bounded Newton iterations
- Price-scale updates should be gradual and profit-gated rather than immediate
- Dynamic fees and oracle observations can share the same invariant state

## Avoid When

- Assets are tightly pegged and a stable invariant is simpler
- Governance or keepers can set the price scale directly without profit gates
- The pool cannot tolerate complex invariant and price-scale tests
- External routers cannot model the pool's dynamic fee and price-scale behavior

## Trade-offs

**Pros:**
- Concentrates liquidity for volatile pairs without a fixed peg assumption
- Lets the pool adapt internal pricing gradually from observed profitable state
- Can pair dynamic fees with price-scale movement to protect LPs

**Cons:**
- Invariant, fee, oracle, and price-scale logic are tightly coupled
- Incorrect profit gates can move value from LPs to traders
- Integrators need exact quote parity with pool math

## How It Works

The pool solves a crypto invariant from balances, amplification, gamma, and price
scale. Swaps update balances and fees, then the pool may adjust the price scale
only when accumulated virtual profit exceeds configured thresholds:

```solidity
xp = scaleBalances(balances, priceScale);
D = newtonInvariant(A, gamma, xp);
amountOut = solveY(D, xpAfterInput);

if (virtualPrice > allowedLoss && profit > adjustmentThreshold) {
    priceScale = moveTowardObservedPrice(priceScale, oraclePrice, adjustmentStep);
}
```

The price-scale adjustment is part of AMM state, not an oracle guarantee.

## Key Points

- Bound Newton invariant and output solvers.
- Gate price-scale movement by virtual profit or a similar LP-protection signal.
- Couple dynamic fee calculation to balance concentration and price-scale state.
- Test price-scale updates across profitable, unprofitable, balanced, and
  imbalanced paths.
- Treat the pool EMA/oracle as AMM state for execution and monitoring, not as a
  manipulation-resistant collateral oracle by itself.
- Parameter research that compares price-scale catch-up, pool imbalance, and virtual-profit behavior should be captured as simulation support, not production evidence, unless it maps to deployed pool code.

## Source Evidence

- Curve Crypto computes the crypto invariant and output balances through bounded
  Newton-style math in `/private/tmp/defillama-source/curvefi__curve-crypto-contract/contracts/two/CurveCryptoSwap2.vy:253-407`.
- Curve Crypto combines swaps, dynamic fees, and price-scale/oracle updates in
  `/private/tmp/defillama-source/curvefi__curve-crypto-contract/contracts/two/CurveCryptoSwap2.vy:466-530`
  and `/private/tmp/defillama-source/curvefi__curve-crypto-contract/contracts/two/CurveCryptoSwap2.vy:610-721`.
- Curve Crypto tests oracle and stateful behavior in
  `/private/tmp/defillama-source/curvefi__curve-crypto-contract/tests/twocrypto/test_oracles.py`
  and `/private/tmp/defillama-source/curvefi__curve-crypto-contract/tests/twocrypto/test_stateful.py`.
- Yield Basis simulations under `/private/tmp/defillama-source/yield-basis__yb-simulations/btcusd` analyze Curve-style price-scale following, imbalance, dynamic rates, and fee variants for BTC/stable pools as simulation-only support for adaptive price-scale trade-offs.

## Related Patterns

- [Amplified Stable Invariant](./pattern-amplified-stable-invariant.md)
- [Off-Peg Dynamic Fee](./pattern-offpeg-dynamic-fee.md)
- [Invariant-Delta Liquidity Accounting](./pattern-invariant-delta-liquidity-accounting.md)
- [TWAP Oracle](../oracles/pattern-twap-oracle.md)
