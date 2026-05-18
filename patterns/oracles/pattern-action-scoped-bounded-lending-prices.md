# Action-Scoped Bounded Lending Prices

> Use conservative bounded prices for borrowing-power checks while using liquidation-specific prices for liquidation eligibility.

## Metadata

| Property | Value |
|----------|-------|
| Category | oracles |
| Tags | oracle, lending, bounded-price, liquidation, collateral-factor |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A lending protocol wants to resist oracle pumps that create new borrow capacity
- Liquidation should not be triggered only because a conservative bounded price is below spot
- Different actions have different risk tolerance
- The risk engine can select price weights by action

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

Borrow, redeem, and transfer checks can use conservative bounded collateral values. Liquidation checks can use liquidation thresholds or spot-like values so bounded-price divergence does not prematurely liquidate accounts.

## Key Points

- Document the price mode used by every user action.
- Test accounts that pass spot checks but fail bounded checks.
- Test accounts between borrow and liquidation thresholds.
- Monitor divergence between bounded and liquidation price modes.
- Pair with collateral threshold separation so action scopes are coherent.

## Source Evidence

- Venus parameterizes liquidity calculations by weight function, uses bounded prices for borrow checks, and uses a liquidation-threshold path for liquidation eligibility.

## Related Patterns

- [Historical Bounds](./pattern-historical-bounds.md)
- [Collateral Threshold Separation Requirements](../lending/req-collateral-threshold-separation.md)
- [Price Manipulation Risk](./risk-price-manipulation.md)
