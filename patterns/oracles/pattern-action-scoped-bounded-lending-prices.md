# Action-Scoped Bounded Risk Prices

> Use action-specific bounded prices or validity flags for borrowing, liquidation, funding, settlement, and margin checks.

## Metadata

| Property | Value |
|----------|-------|
| Category | oracles |
| Tags | oracle, lending, perps, bounded-price, liquidation, collateral-factor |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A lending protocol wants to resist oracle pumps that create new borrow capacity
- Liquidation should not be triggered only because a conservative bounded price is below spot
- Different actions have different risk tolerance
- The risk engine can select price weights by action
- A perps market wants different validity requirements for funding, settlement, margin, liquidation, trigger, or AMM-fill paths

## Avoid When

- One price source and one collateral threshold are intentionally used for all actions
- Price paths are undocumented or hard for liquidators to reproduce
- Bounded prices can become stale or manipulable without monitoring

## Trade-offs

**Pros:**
- Oracle pumps cannot mint new borrow capacity while liquidation still uses spot-like values, so the two risks are tuned independently.
- Each action fails closed on exactly the validity checks it needs instead of one global freshness rule.
- Liquidations can still resolve risk during partial oracle degradation by requiring a narrower flag set.
- Per-token borrow, collateral, and liquidation factors give granular risk tuning without forking the oracle.

**Cons:**
- Multiplies the test and documentation matrix: every action x price-mode combination must be specified, tested, and monitored.
- Liquidators and integrators must reproduce per-action price logic off-chain, raising integration cost and error rates.
- Misconfigured flag masks or factors silently create fail-open paths (e.g. stale-price withdrawals on debt-bearing accounts).
- Sustained divergence between bounded and liquidation price modes can leave accounts over-borrowed yet not liquidatable until someone notices.
- Without hard bounds, per-token per-action factors drift toward discretionary admin pricing.

## How It Works

Parameterize liquidity calculations by action:

```solidity
function borrowAllowed(address account, uint256 amount) external view returns (bool) {
    return liquidity(account, PriceMode.BOUNDED_COLLATERAL_FACTOR) >= amount;
}

function liquidateAllowed(address account) external view returns (bool) {
    return liquidity(account, PriceMode.LIQUIDATION_THRESHOLD) < 0;
}
```

Borrow, redeem, and transfer checks can use conservative bounded collateral values. Liquidation checks can use liquidation thresholds or spot-like values so bounded-price divergence does not prematurely liquidate accounts. Some designs deliberately choose a stricter liquidation price, such as a lower bounded price, as a risk posture; that should be documented as a stricter liquidation policy rather than merged into borrower-grace guidance.

Lending protocols can express the same action split as token-specific valuation
factors. Borrow checks inflate debt value with a borrow factor, collateral
checks discount wrapped collateral by a collateral factor, and liquidation
conversion can apply a liquidation incentive factor. Those factors should be
bounded at onboarding and read through the same oracle path used by the health
check.

The same idea can be represented as validation-status flags attached to the oracle value:

```solidity
function priceFor(Action action, address asset) internal view returns (uint256 price) {
    Price memory p = oracle.price(asset);
    require(p.flags & requiredFlags[action] == requiredFlags[action], "price flags");
    return p.value;
}
```

Borrowing may require all freshness, confidence, TWAP, and heuristic checks. Liquidation may require a narrower liquidation-safe flag set so accounts can still be resolved during partial oracle degradation.

Some credit-account systems use a "safe price" only for post-operation checks
after a user or adapter could have offloaded mispriced collateral. A safe price
can be the lower of a main feed and reserve feed; missing reserve data should
return zero only in paths where zero will fail the collateral check, not in
general-purpose price reads.

Collateral-only exits can sometimes use a narrower stale-price policy, but only
when the account has no debt and the action cannot increase protocol credit
risk. Debt-bearing withdraw, borrow, transfer, and liquidation paths should fail
closed if their action-required price flags are missing.

For perps, action-scoped validity can require different confidence, staleness,
volatility, divergence, and settlement-heartbeat checks by action:

```rust
fn oracle_valid_for(action: Action, oracle: OracleStatus) -> bool {
    match action {
        Action::Funding => oracle.fresh && oracle.confidence_ok,
        Action::Liquidation => oracle.fresh && oracle.not_too_volatile && oracle.mark_divergence_ok,
        Action::Settlement => oracle.fresh && oracle.settlement_heartbeat_ok,
        Action::AmmFill => oracle.fresh && oracle.mark_divergence_ok,
    }
}
```

Collateral haircuts can also be action-scoped. For example, a perps engine can
discount non-USD collateral by trade size relative to a spot-market skew scale,
with bounded minimum and maximum discounts and separate staleness tolerance for
the collateral path.

## Key Points

- Document the price mode used by every user action.
- Test accounts that pass spot checks but fail bounded checks.
- Test accounts between borrow and liquidation thresholds.
- Monitor divergence between bounded and liquidation price modes.
- Pair with collateral threshold separation so action scopes are coherent.
- Bound borrow, collateral, and liquidation factors so action-scoped prices cannot become discretionary admin pricing.
- If using status flags, document the required flag mask for each action and test that missing action-required flags fail closed.
- If allowing stale-price collateral withdrawals, test the no-debt and with-debt branches separately.
- For perps, test each oracle action class separately; do not assume a funding-safe price is liquidation-safe or settlement-safe.
- For stable-asset mint/redeem paths, choose conservative peg bounds by action: minting can use the lower of oracle and par, while redemption can use the higher of oracle and par only if reserves and caps absorb the difference.
- Borrower-favorable LTV oracle changes should be ramped and monotonic, with liquidation-threshold separation preserved, rather than treated as ordinary price freshness.
- For stable-asset redemption that pays a basket of reserves, use oracle values
  to decide global collateral-ratio penalties, not to silently reweight each
  output token away from the pro-rata reserve claim.
- For credit accounts, request safe prices only on paths where a zero or missing
  reserve feed should fail closed.
- For non-USD perps collateral, bind haircut configuration to action-specific
  price freshness and trade-size/skew bounds.
- Lending systems with separate max-LTV and solvency oracle paths should test
  deposit, borrow, transition, liquidation, and collateral-exit actions against
  the exact oracle mode each action uses.
- Long-tail or NFT collateral can attach TWAP and freshness state to
  collection-level prices; borrow and auction entry should fail closed on stale
  or missing collection data.
- Historical-low dampening is an action-scoped borrowing-power policy, not a
  general market price: document where the dampened value is used and where
  spot-like values remain acceptable.

## Source Evidence

- Venus parameterizes liquidity calculations by weight function, uses bounded prices for borrow checks, and uses a liquidation-threshold path for liquidation eligibility.
- Kamino Lend attaches price status flags to oracle values and uses different required flag sets for borrow and liquidation paths.
- Suilend permits stale-price collateral exits only for no-debt accounts while debt-bearing withdrawal and borrow paths fail closed; evidence appears in [`contracts/suilend/sources/obligation.move`](https://github.com/suilend/suilend/blob/d5ba83a617bb0778b48b0c3b1e77a87be81258ca/contracts/suilend/sources/obligation.move) and oracle checks in `oracles.move`.
- fx Protocol uses min/mid/max bounded prices and action modes for exchange, redeem, and liquidation in [`contracts/price-oracle`](https://github.com/AladdinDAO/fx-protocol-contracts/blob/5e198e93657db008a57129e7eea21a996618f17f/contracts/price-oracle) and `contracts/core/PoolConfiguration.sol`.
- Drift uses action-scoped oracle validity for funding, settlement, liquidation, margin, trigger, and AMM-fill paths in [`programs/drift/src/math/oracle.rs`](https://github.com/drift-labs/protocol-v2/blob/0ae3e3b1db782a6765c3525b3dec38ad4d9d3a62/programs/drift/src/math/oracle.rs).
- Alpha Homora V2 uses token-specific borrow, collateral, and liquidation factors around a shared source oracle in [`contracts/oracle/ProxyOracle.sol`](https://github.com/AlphaFinanceLab/alpha-homora-v2-contract/blob/f74fc460bd614ad15bbef57c88f6b470e5efd1fd/contracts/oracle/ProxyOracle.sol) and applies them in HomoraBank health and liquidation checks.
- Satoshi Nexus prices stable-asset minting with conservative peg caps and redemptions with the opposite conservative bound in [`src/core/NexusYieldManager.sol`](https://github.com/Satoshi-Protocol/satoshi-core/blob/7f5eddaed965904fde10ea1d40c4c4b3ea118ada/src/core/NexusYieldManager.sol).
- Fraxlend stores low/high oracle exchange rates with deviation gating, uses the high price for solvency checks and the low price for liquidation calculations in [`src/contracts/FraxlendPairCore.sol`](https://github.com/FraxFinance/fraxlend/blob/2bed49d4dcc6702d92dede825c3424893517d841/src/contracts/FraxlendPairCore.sol).
- Frax FPI controller tests peg-band mint, redeem, and TWAMM actions against bounded prices in [`src/hardhat/contracts/FPI/FPIControllerPool.sol`](https://github.com/FraxFinance/frax-solidity/blob/30532c8cefcbf5c7efafcff4369261bd435a4859/src/hardhat/contracts/FPI/FPIControllerPool.sol).
- Olympus Cooler V2 uses an LTV oracle for origination and liquidation thresholds and constrains borrower-favorable changes in [`src/policies/cooler/CoolerLtvOracle.sol`](https://github.com/OlympusDAO/olympus-v3/blob/120266b021f1eaa0c46b00af0114bd47bbc9e590/src/policies/cooler/CoolerLtvOracle.sol).
- Angle Transmuter uses action-specific stable-asset oracle bounds for swap and
  mint/burn paths, while redemption uses oracle value to compute the global
  collateral-ratio penalty rather than per-token output weights in
  [`contracts/transmuter/libraries/LibOracle.sol:23-91`](https://github.com/angleprotocol/angle-transmuter/blob/2fa74b73a3f5aa921e619e55744d73228cd2fe71/contracts/transmuter/libraries/LibOracle.sol#L23-L91),
  [`contracts/transmuter/libraries/LibOracle.sol:104-150`](https://github.com/angleprotocol/angle-transmuter/blob/2fa74b73a3f5aa921e619e55744d73228cd2fe71/contracts/transmuter/libraries/LibOracle.sol#L104-L150),
  and [`contracts/transmuter/facets/Swapper.sol:236-276`](https://github.com/angleprotocol/angle-transmuter/blob/2fa74b73a3f5aa921e619e55744d73228cd2fe71/contracts/transmuter/facets/Swapper.sol#L236-L276).
- Gearbox V3 derives safe prices from main and reserve feeds and uses them for
  post-operation credit-account checks after risky adapter operations in
  [`contracts/core/PriceOracleV3.sol:24-35`](https://github.com/gearbox-protocol/core-v3/blob/b038597d9070d9fd18593a6ae9c3d28ca931bb73/contracts/core/PriceOracleV3.sol#L24-L35),
  [`contracts/core/PriceOracleV3.sol:127-179`](https://github.com/gearbox-protocol/core-v3/blob/b038597d9070d9fd18593a6ae9c3d28ca931bb73/contracts/core/PriceOracleV3.sol#L127-L179),
  and [`contracts/credit/CreditFacadeV3.sol:625-649`](https://github.com/gearbox-protocol/core-v3/blob/b038597d9070d9fd18593a6ae9c3d28ca931bb73/contracts/credit/CreditFacadeV3.sol#L625-L649).
- Synthetix V3 perps collateral configuration applies bounded non-USD collateral
  discounts by trade size and skew scale in [`markets/perps-market/contracts/storage/PerpsCollateralConfiguration.sol:23-48`](https://github.com/synthetixio/synthetix-v3/blob/23585f73c76d625b2a43aaf94dc440a8a1e7a8fa/markets/perps-market/contracts/storage/PerpsCollateralConfiguration.sol#L23-L48)
  and [`markets/perps-market/contracts/storage/PerpsCollateralConfiguration.sol:128-157`](https://github.com/synthetixio/synthetix-v3/blob/23585f73c76d625b2a43aaf94dc440a8a1e7a8fa/markets/perps-market/contracts/storage/PerpsCollateralConfiguration.sol#L128-L157).
- Silo V2 separates max-LTV and solvency oracle configuration in [`silo-core/contracts/SiloConfig.sol`](https://github.com/silo-finance/silo-contracts-v2/blob/fd1c73beafb7c81f77cd4477002ebadb4142d243/silo-core/contracts/SiloConfig.sol) and applies action logic through [`silo-core/contracts/lib/Actions.sol`](https://github.com/silo-finance/silo-contracts-v2/blob/fd1c73beafb7c81f77cd4477002ebadb4142d243/silo-core/contracts/lib/Actions.sol).
- Inverse FiRM dampens borrower credit by recent daily lows in [`src/Oracle.sol`](https://github.com/InverseFinance/FiRM/blob/6cd9f06cd0da79ccaad9f663aed299ef3021af10/src/Oracle.sol) and consumes that bounded price in [`src/Market.sol`](https://github.com/InverseFinance/FiRM/blob/6cd9f06cd0da79ccaad9f663aed299ef3021af10/src/Market.sol).
- BendDAO stores NFT collection price records, calculates TWAP values, and uses freshness-aware validation around borrow and auction paths in [`contracts/protocol/NFTOracle.sol`](https://github.com/BendDAO/bend-lending-protocol/blob/81c90c06373bd6cc616ed0d0712fe382cad56548/contracts/protocol/NFTOracle.sol) and [`contracts/libraries/logic/ValidationLogic.sol`](https://github.com/BendDAO/bend-lending-protocol/blob/81c90c06373bd6cc616ed0d0712fe382cad56548/contracts/libraries/logic/ValidationLogic.sol).

## Related Patterns

- [Historical Bounds](./pattern-historical-bounds.md)
- [Collateral Threshold Separation Requirements](../lending/req-collateral-threshold-separation.md)
- [Price Manipulation Risk](./risk-price-manipulation.md)
- [Oracle Reliability Requirements](./req-oracle-reliability.md)
