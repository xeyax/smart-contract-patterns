# Exchange-Rate Valuation Risk

> Valuing collateral by a protocol exchange rate can make fresh prices look safe while ignoring market depeg or redemption impairment.

## Metadata

| Property | Value |
|----------|-------|
| Category | oracles |
| Tags | oracle, exchange-rate, lst, lrt, erc4626, depeg, risk |
| Type | Risk Description |

## Problem Description

Some collateral assets expose a fresh exchange rate from internal accounting, staking conversions, or ERC4626 `convertToAssets`. That value may be up to date and still not represent the asset's market-clearing price.

This is especially dangerous for LSTs, LRTs, vault shares, and wrappers where redemption can be delayed, capped, or impaired. A lending market can treat the collateral as fully backed while secondary markets price it at a discount.

## Applies When

- Collateral value comes from staking, vault, or wrapper exchange rates
- Collateral value comes from AMM LP virtual price or invariant value per share
- Redemptions are delayed, queued, capped, or permissioned
- Liquidations sell collateral into a market price, not into the exchange-rate redemption path
- The oracle reports a fresh timestamp but no market discount

## Requirements Affected

This risk affects [Oracle Reliability Requirements](./req-oracle-reliability.md):
- **R2: Accuracy** - fresh exchange rates can diverge from realizable market value
- **R3: Manipulation Resistance** - the source may be hard to manipulate but still economically incomplete

## Failure Modes

- Borrowers pledge vault shares valued at internal NAV while market bids are discounted.
- Liquidators refuse to buy collateral at oracle value, leaving bad debt.
- A wrapper updates `updatedAt` every call while the underlying redemption path is impaired.
- A protocol caps upward movement but ignores downside depeg.
- A metapool treats base-pool LP virtual price as fair value while secondary market liquidity is thin or cached.
- A liquid-staking token's internal exchange rate is fresh and bounded, but withdrawals are delayed or market buyers discount the token.

## Mitigations

- Cross-check exchange rate against market TWAP or liquidity-aware price.
- Apply conservative loan-to-value discounts for delayed or permissioned redemption.
- Monitor both fair-value ratio and market ratio.
- Pause new borrowing or reduce caps when market price diverges from exchange rate.
- Document whether liquidations assume redemption value or market-sale value.
- For LSTs, separately monitor total supply, delegated backing, exchange-rate drops, and withdrawal queue liveness.

## Source Evidence

- SparkLend Advanced includes exchange-rate style valuation components for stable, LST, LRT, and ERC4626-style assets, which surfaced the need to distinguish freshness from realizable market value.
- Curve metapools cache and read base-pool LP virtual prices, which are useful fair-value accounting inputs but are not market-clearing prices.
- Stader BNBx derives a fresh internal LST exchange rate from delegated backing and token supply, which is useful for mint/redeem accounting but still distinct from market-clearing collateral value.

## Related Patterns

- [Peg Ratio Monitor](./pattern-peg-ratio-monitor.md)
- [Historical Bounds](./pattern-historical-bounds.md)
- [LP Virtual Price Monotonicity Requirements](../liquidity/req-lp-virtual-price-monotonicity.md)
- [Price Manipulation Risk](./risk-price-manipulation.md)
