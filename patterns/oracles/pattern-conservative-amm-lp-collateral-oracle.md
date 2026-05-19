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

For constant-product and weighted pools, the conservative value can be derived
from fair reserves instead of current reserve ratios. A Uniswap-style LP oracle
can price `2 * sqrt(px0 * px1) * sqrt(reserve0 * reserve1) / totalSupply`, while
a weighted-pool oracle can solve for fair reserves under the pool invariant and
external prices before dividing by LP supply.

## Key Points

- Check external feed positivity, freshness, and L2 sequencer status where relevant.
- Use conservative constituent pricing such as `min(price_i)` for stableswap-style pools when appropriate.
- For constant-product and weighted pools, derive fair reserves from the invariant and external prices instead of trusting the current manipulated reserve split.
- Document read-only reentrancy assumptions for pool view functions.
- Apply collateral discounts for redemption delay, market depeg, and thin LP liquidity.
- Regression-test every configured pool and feed route.
- Do not use internal virtual price as a market-clearing price.

## Source Evidence

- Stake DAO's Curve stableswap collateral oracle uses conservative pool pricing with external feed hops and explicitly documents flash-manipulation, read-only reentrancy, and L2 sequencer caveats.
- Alpha Homora V2 prices Uniswap V2 LP collateral from the square-root reserve invariant, Balancer LP collateral from fair reserves, and Curve LP collateral from the minimum underlying price times virtual price in `/private/tmp/defillama-source/AlphaFinanceLab__alpha-homora-v2-contract/contracts/oracle`.
- Satoshi Core's Uniswap V2 LP feed normalizes reserve and feed decimals before applying a square-root reserve invariant, while its Curve LP feed reads virtual price after a zero-liquidity removal checkpoint in `/private/tmp/defillama-source/Satoshi-Protocol__satoshi-core/src/dependencies/priceFeed`.

## Related Patterns

- [Exchange-Rate Valuation Risk](./risk-exchange-rate-valuation.md)
- [Multi-Source Validation](./pattern-multi-source-validation.md)
- [LP Virtual Price Monotonicity Requirements](../liquidity/req-lp-virtual-price-monotonicity.md)
