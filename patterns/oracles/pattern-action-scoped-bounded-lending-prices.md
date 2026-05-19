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

The same idea can be represented as validation-status flags attached to the oracle value:

```solidity
function priceFor(Action action, address asset) internal view returns (uint256 price) {
    Price memory p = oracle.price(asset);
    require(p.flags & requiredFlags[action] == requiredFlags[action], "price flags");
    return p.value;
}
```

Borrowing may require all freshness, confidence, TWAP, and heuristic checks. Liquidation may require a narrower liquidation-safe flag set so accounts can still be resolved during partial oracle degradation.

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

## Key Points

- Document the price mode used by every user action.
- Test accounts that pass spot checks but fail bounded checks.
- Test accounts between borrow and liquidation thresholds.
- Monitor divergence between bounded and liquidation price modes.
- Pair with collateral threshold separation so action scopes are coherent.
- If using status flags, document the required flag mask for each action and test that missing action-required flags fail closed.
- If allowing stale-price collateral withdrawals, test the no-debt and with-debt branches separately.
- For perps, test each oracle action class separately; do not assume a funding-safe price is liquidation-safe or settlement-safe.

## Source Evidence

- Venus parameterizes liquidity calculations by weight function, uses bounded prices for borrow checks, and uses a liquidation-threshold path for liquidation eligibility.
- Kamino Lend attaches price status flags to oracle values and uses different required flag sets for borrow and liquidation paths.
- Suilend permits stale-price collateral exits only for no-debt accounts while debt-bearing withdrawal and borrow paths fail closed; evidence appears in `/private/tmp/defillama-source/suilend__suilend/contracts/suilend/sources/obligation.move` and oracle checks in `oracles.move`.
- fx Protocol uses min/mid/max bounded prices and action modes for exchange, redeem, and liquidation in `/private/tmp/defillama-source/AladdinDAO__fx-protocol-contracts/contracts/price-oracle` and `contracts/core/PoolConfiguration.sol`.
- Drift uses action-scoped oracle validity for funding, settlement, liquidation, margin, trigger, and AMM-fill paths in `/private/tmp/defillama-source/drift-labs__protocol-v2/programs/drift/src/math/oracle.rs`.

## Related Patterns

- [Historical Bounds](./pattern-historical-bounds.md)
- [Collateral Threshold Separation Requirements](../lending/req-collateral-threshold-separation.md)
- [Price Manipulation Risk](./risk-price-manipulation.md)
- [Oracle Reliability Requirements](./req-oracle-reliability.md)
