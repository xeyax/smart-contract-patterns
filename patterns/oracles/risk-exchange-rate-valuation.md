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
- A multi-LST router preserves value under configured calculators while market prices or withdrawal fees make those rates unrealizable.
- An upgrade-slot-pinned adapter detects upstream semantic changes but still depends on governance to accept or reject the new valuation semantics.
- A savings token's internal conversion rate increases deterministically while levered lending markets depend on liquidators realizing secondary-market value.
- Principal/yield tokens or fixed-maturity LP tokens report accounting rates derived from exchange-rate and maturity math, but liquidation still depends on realizable PT/YT/LP market value.
- ERC4626 share valuation recursively depends on the underlying asset oracle and redemption semantics, not only `convertToAssets`.
- AMM vaults scale raw balances by token decimals and rate providers for pool
  math, yield fees, or LP-rate views; those scaled balances are accounting inputs
  and should not be treated as market-clearing collateral prices.
- Chainlink-compatible oracles that sample ERC4626 `convertToAssets` inherit
  vault donation, offset, and share-price semantics; interface compatibility
  does not turn a vault conversion into a market-clearing price.

## Mitigations

- Cross-check exchange rate against market TWAP or liquidity-aware price.
- Apply conservative loan-to-value discounts for delayed or permissioned redemption.
- Monitor both fair-value ratio and market ratio.
- Pause new borrowing or reduce caps when market price diverges from exchange rate.
- Document whether liquidations assume redemption value or market-sale value.
- For LSTs, separately monitor total supply, delegated backing, exchange-rate drops, and withdrawal queue liveness.
- For AMM LP collateral, combine virtual-price or invariant value with conservative constituent pricing and explicit read-only reentrancy and sequencer checks.
- Treat calculator value preservation as accounting protection, not market-price protection.
- Monitor upstream program upgrades and adapter slot acceptance when valuations depend on upgradeable Solana programs.
- For ERC4626 registries, require the underlying asset to be registered and prevent removal while dependent vault shares remain active.
- Haircut principal/yield or LP rates when the yield-source exchange rate drops below the stored index, and document whether LP values are approximate accounting values.
- For AMM vault rate providers, separate "pool math and fee accounting rate" from
  "oracle price for liquidation" and document whether BPT/share rates are
  monotonic, cached, or hook-adjusted.
- When ERC4626 share price feeds are used, separately evaluate donation
  sensitivity, offset strength, and the underlying asset oracle.

## Source Evidence

- SparkLend Advanced includes exchange-rate style valuation components for stable, LST, LRT, and ERC4626-style assets, which surfaced the need to distinguish freshness from realizable market value.
- Curve metapools cache and read base-pool LP virtual prices, which are useful fair-value accounting inputs but are not market-clearing prices.
- Stader BNBx derives a fresh internal LST exchange rate from delegated backing and token supply, which is useful for mint/redeem accounting but still distinct from market-clearing collateral value.
- Stake DAO's Curve LP collateral oracle documents conservative stableswap pricing while preserving read-only reentrancy, sequencer, and market-value caveats.
- Sanctum demonstrates conservative LST router accounting and upgrade-slot-pinned rate adapters, both of which protect internal valuation semantics without proving market-clearing price.
- Reservoir sRUSD loopers value collateral through internal saving-module conversion paths while Morpho market parameters determine liquidation exposure in [`src`](https://github.com/reservoir-protocol/srusd-loop/blob/f97aaab1ff1028601e2fa888f1161978cf3711ed/src).
- Pendle's PT/YT/LP oracle libraries haircut rates when the standardized-yield exchange rate drops below the stored PY index and document LP output as approximate in [`contracts/oracles/PtYtLpOracle`](https://github.com/pendle-finance/pendle-core-v2-public/blob/fdcfe39ed7b45717f0e6e286581bdcf96bb2f9ce/contracts/oracles/PtYtLpOracle).
- Aera v2 values ERC4626 shares through `convertToAssets` and the underlying asset oracle, requires underlying registration, and blocks removal of active underlying assets in [`v2`](https://github.com/aera-finance/aera-contracts-public/blob/9888a9e0d50fa38d4e86a69a8ebb9b605b08dafd/v2).
- Balancer V3 scales token balances by decimal and rate-provider data for pool
  math, yield fees, and BPT-rate views in [`pkg/vault/contracts/Vault.sol:169-190`](https://github.com/balancer/balancer-v3-monorepo/blob/0a5890a8c5d79865498d75cdc6ecdc75cf8d297d/pkg/vault/contracts/Vault.sol#L169-L190),
  [`pkg/vault/contracts/lib/PoolDataLib.sol:31-92`](https://github.com/balancer/balancer-v3-monorepo/blob/0a5890a8c5d79865498d75cdc6ecdc75cf8d297d/pkg/vault/contracts/lib/PoolDataLib.sol#L31-L92),
  and [`pkg/vault/contracts/VaultExtension.sol:491-511`](https://github.com/balancer/balancer-v3-monorepo/blob/0a5890a8c5d79865498d75cdc6ecdc75cf8d297d/pkg/vault/contracts/VaultExtension.sol#L491-L511);
  this is accounting evidence, not proof of market-clearing LP value.
- Balancer V2 composable stable pools expose rate-derived BPT math in
  [`pkg/pool-stable/contracts/ComposableStablePoolRates.sol:38-65`](https://github.com/balancer/balancer-v2-monorepo/blob/316ded078ddc2f1b28da5804d25752af67453435/pkg/pool-stable/contracts/ComposableStablePoolRates.sol#L38-L65)
  and [`pkg/pool-stable/contracts/ComposableStablePoolRates.sol:197-280`](https://github.com/balancer/balancer-v2-monorepo/blob/316ded078ddc2f1b28da5804d25752af67453435/pkg/pool-stable/contracts/ComposableStablePoolRates.sol#L197-L280).
- Morpho Blue oracle wrappers sample ERC4626 conversions and warn about donation
  effects in [`src/morpho-chainlink/MorphoChainlinkOracleV2.sol:52`](https://github.com/morpho-org/morpho-blue-oracles/blob/e32d8902f9518365caa53e9eaed3cbd6cb017a63/src/morpho-chainlink/MorphoChainlinkOracleV2.sol#L52)
  and [`src/morpho-chainlink/libraries/VaultLib.sol:11`](https://github.com/morpho-org/morpho-blue-oracles/blob/e32d8902f9518365caa53e9eaed3cbd6cb017a63/src/morpho-chainlink/libraries/VaultLib.sol#L11).

## Related Patterns

- [Peg Ratio Monitor](./pattern-peg-ratio-monitor.md)
- [Historical Bounds](./pattern-historical-bounds.md)
- [Conservative AMM LP Collateral Oracle](./pattern-conservative-amm-lp-collateral-oracle.md)
- [LP Virtual Price Monotonicity Requirements](../liquidity/req-lp-virtual-price-monotonicity.md)
- [Price Manipulation Risk](./risk-price-manipulation.md)
