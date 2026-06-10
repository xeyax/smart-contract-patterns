# Off-Peg Dynamic Fee

> Increase AMM fees as pool balances move away from the expected peg or balance so trades that worsen imbalance pay more.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, fee, imbalance, peg, stable-swap |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Pool assets are expected to stay close to a peg or fair ratio
- Trades that worsen imbalance increase LP risk
- A static fee underprices off-peg inventory risk
- Fee parameters can be bounded and monitored

## Avoid When

- Assets are volatile and no peg or target balance exists
- Dynamic fees would make user quotes unpredictable without protection
- Governance can set fee multipliers without bounds

## Trade-offs

**Pros:**
- Trades that worsen imbalance pay for the inventory risk they create, compensating LPs when it matters most.
- Higher off-peg fees dampen one-sided drain during depeg stress, buying time without halting the pool.
- The fee is a pure function of pool balances — no oracle, keeper, or external volatility input needed.
- Bounded multiplier and max-fee caps keep the worst-case cost analyzable for integrators.

**Cons:**
- Quotes become state-dependent: the fee can shift between quote and execution, so users need slippage protection and aggregators need imbalance-aware quoting.
- Rising fees can mask a permanent depeg as "expensive but functional," delaying circuit-breaker response if not paired with caps or breakers.
- Fee multiplier becomes an economic risk parameter; ungoverned or unbounded changes can gate exits behind punitive fees.
- Consistent application across swaps, imbalanced deposits, and imbalanced withdrawals multiplies the code paths to test; a missed path becomes a cheap imbalance route.
- Concentration-based variants add invariant-coupled fee math that is harder to reason about than simple peg deviation.

## How It Works

Scale fees by a function of balance imbalance:

```solidity
uint256 imbalance = deviationFromTarget(balancesAfterTrade);
uint256 dynamicFee = baseFee + imbalance * feeMultiplier / BPS;
require(dynamicFee <= maxFee, "fee too high");
```

The fee applies to swaps and liquidity operations that create or increase imbalance.

Crypto-invariant pools can also scale fees by balance concentration. Instead of
a simple peg deviation, the fee rises as liquidity concentrates on one side of
the invariant, then falls as balances return to the target range.

## Key Points

- Bound fee multipliers and maximum fees.
- Quote dynamic fees before execution and enforce user slippage limits.
- Apply the fee consistently to swaps, imbalanced deposits, and imbalanced withdrawals.
- For concentration-based fees, test fee behavior at balanced, mildly
  imbalanced, and severely concentrated states.
- Avoid using fee increases to hide permanent depeg; pair with circuit breakers or caps.
- Test balanced, mildly off-peg, severely off-peg, and parameter-change cases.

## Source Evidence

- Curve Aave-style pools scale fees by balance imbalance and test bounded fee multiplier changes.
- Curve StableSwap NG applies off-peg fee multipliers in [`contracts/main/CurveStableSwapNG.vy:885-900`](https://github.com/curvefi/stableswap-ng/blob/2abe778f40206a6c0fd108a0a53ad3266cbedeee/contracts/main/CurveStableSwapNG.vy#L885-L900).
- Curve Crypto applies a balance-concentration dynamic fee in
  [`contracts/two/CurveCryptoSwap2.vy:515-530`](https://github.com/curvefi/curve-crypto-contract/blob/d7d04cd9ae038970e40be850df99de8c1ff7241b/contracts/two/CurveCryptoSwap2.vy#L515-L530).

## Related Patterns

- [Dynamic Premium](../vaults/pattern-dynamic-premium.md)
- [Hook-Governed Dynamic LP Fee](./pattern-hook-governed-dynamic-lp-fee.md)
- [Amplified Stable Invariant](./pattern-amplified-stable-invariant.md)
- [Peg Ratio Monitor](../oracles/pattern-peg-ratio-monitor.md)
