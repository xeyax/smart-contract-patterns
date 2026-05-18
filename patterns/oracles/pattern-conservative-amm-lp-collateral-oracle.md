# Conservative AMM LP Collateral Oracle

> Price AMM LP collateral with conservative pool-internal pricing plus fresh external feed hops, while preserving exchange-rate and reentrancy caveats.

## Metadata

| Property | Value |
|----------|-------|
| Category | oracles |
| Tags | oracle, amm, lp-token, collateral, curve, lending |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A lending market accepts curated AMM LP tokens as collateral
- The pool exposes a manipulation-resistant virtual price or invariant value
- Constituent assets have fresh external feeds
- The protocol can discount or cap collateral value for liquidity and redemption risk

## Avoid When

- Pool virtual price is manipulable in the same transaction
- External feeds lack staleness, sequencer, or positivity checks
- LP collateral must be liquidated into thin secondary markets
- The oracle cannot handle read-only reentrancy or pool-specific edge cases

## How It Works

Use the most conservative constituent value and multiply by a checked LP fair-value input:

```solidity
function lpPrice() external view returns (uint256) {
    uint256 minAssetPrice = min(_freshFeed(asset0), _freshFeed(asset1));
    uint256 virtualPrice = pool.get_virtual_price();
    require(_poolReadIsSafe(), "pool read");
    return minAssetPrice * virtualPrice / WAD;
}
```

This estimates a fair-value floor for curated pools. It does not prove the LP token can be liquidated at that value during stress.

## Key Points

- Check external feed positivity, freshness, and L2 sequencer status where relevant.
- Use conservative constituent pricing such as `min(price_i)` for stableswap-style pools when appropriate.
- Document read-only reentrancy assumptions for pool view functions.
- Apply collateral discounts for redemption delay, market depeg, and thin LP liquidity.
- Regression-test every configured pool and feed route.
- Do not use internal virtual price as a market-clearing price.

## Source Evidence

- Stake DAO's Curve stableswap collateral oracle uses conservative pool pricing with external feed hops and explicitly documents flash-manipulation, read-only reentrancy, and L2 sequencer caveats.

## Related Patterns

- [Exchange-Rate Valuation Risk](./risk-exchange-rate-valuation.md)
- [Multi-Source Validation](./pattern-multi-source-validation.md)
- [LP Virtual Price Monotonicity Requirements](../liquidity/req-lp-virtual-price-monotonicity.md)
