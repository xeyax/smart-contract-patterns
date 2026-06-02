# Peg Ratio Monitor

> Track normalized market-price and fair-value ratios for pegged or redeemable assets so operators can detect depeg before it becomes bad debt.

## Metadata

| Property | Value |
|----------|-------|
| Category | oracles |
| Tags | oracle, monitoring, peg, stablecoin, lst, ratio |
| Complexity | Low |
| Gas Efficiency | Medium |
| Audit Risk | Low |

## Use When

- An asset should trade near a peg, redemption value, or exchange-rate value
- The protocol needs monitoring before changing caps, rates, or pause state
- A ratio is advisory and should not be mistaken for a liquidation oracle
- Market and fair-value sources are both available

## Avoid When

- The ratio directly prices user operations without manipulation resistance
- The asset does not have a meaningful reference value
- Operators will not act on ratio alerts

## How It Works

Normalize market price against fair value:

```solidity
function pegRatio() external view returns (uint256) {
    uint256 market = marketOracle.price();      // e.g. DEX TWAP or Chainlink
    uint256 fair = exchangeRateOracle.price();  // e.g. redemption value
    require(fair > 0, "bad fair value");
    return market * 1e18 / fair;
}
```

The output is most useful for monitoring, cap changes, and risk dashboards. If used on-chain, treat threshold crossings as circuit-breaker signals rather than precise execution prices.

## Key Points

- Keep source timestamps and decimals visible.
- Alert on both downside depeg and suspicious premium.
- Do not use a short-window spot source for automated liquidations.
- Pair alerts with predefined risk actions such as cap reduction, borrow pause, or higher collateral discount.
- Test stale, zero, and mismatched-decimal source behavior.

## Source Evidence

- SparkLend Advanced includes normalized market/fair ratio monitoring components for assets where peg or exchange-rate divergence matters to lending risk.

## Related Patterns

- [Exchange-Rate Valuation Risk](./risk-exchange-rate-valuation.md)
- [Multi-Source Validation](./pattern-multi-source-validation.md)
- [Historical Bounds](./pattern-historical-bounds.md)
