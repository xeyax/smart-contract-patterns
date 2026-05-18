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

## How It Works

Scale fees by a function of balance imbalance:

```solidity
uint256 imbalance = deviationFromTarget(balancesAfterTrade);
uint256 dynamicFee = baseFee + imbalance * feeMultiplier / BPS;
require(dynamicFee <= maxFee, "fee too high");
```

The fee applies to swaps and liquidity operations that create or increase imbalance.

## Key Points

- Bound fee multipliers and maximum fees.
- Quote dynamic fees before execution and enforce user slippage limits.
- Apply the fee consistently to swaps, imbalanced deposits, and imbalanced withdrawals.
- Avoid using fee increases to hide permanent depeg; pair with circuit breakers or caps.
- Test balanced, mildly off-peg, severely off-peg, and parameter-change cases.

## Source Evidence

- Curve Aave-style pools scale fees by balance imbalance and test bounded fee multiplier changes.

## Related Patterns

- [Dynamic Premium](../vaults/pattern-dynamic-premium.md)
- [Hook-Governed Dynamic LP Fee](./pattern-hook-governed-dynamic-lp-fee.md)
- [Amplified Stable Invariant](./pattern-amplified-stable-invariant.md)
- [Peg Ratio Monitor](../oracles/pattern-peg-ratio-monitor.md)
