# Reserve Exposure Caps

> Bound how much a lending market can supply, borrow, or expose to one asset so risk parameters cannot rely on liquidation mechanics alone.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, risk, supply-cap, borrow-cap, exposure, reserve |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- A market lists assets with limited liquidity or correlated risk
- Governance wants to grow exposure gradually after listing
- Liquidation capacity is smaller than possible supplied or borrowed size
- A protocol needs different caps for supply, borrow, isolation, or debt ceilings

## Avoid When

- The asset is not borrowable and has no protocol exposure beyond custody
- Caps cannot be updated safely as liquidity changes
- Users can bypass caps through wrappers, portals, or alternate markets

## How It Works

Apply cap checks before state changes:

```solidity
function supply(uint256 amount) external {
    accrueInterest();
    require(totalSupplyAssets + amount <= supplyCap, "supply cap");
    _supply(msg.sender, amount);
}

function borrow(uint256 amount) external {
    accrueInterest();
    require(totalBorrowAssets + amount <= borrowCap, "borrow cap");
    _borrow(msg.sender, amount);
}
```

For isolated assets, aggregate exposure can be capped separately from the market's local borrow amount.

## Key Points

- Treat cap increases as high-risk governance actions.
- Define whether accrued interest can push totals above the cap.
- Check caps on mint, borrow, portal, migration, and collateral-enabling paths.
- Pair caps with correlated collateral limits when assets share the same failure mode.
- Monitor cap utilization before listing changes or rate model updates.

## Source Evidence

- Aave V3 uses reserve-level supply and borrow caps, isolation-mode debt ceilings, and exposure controls alongside liquidation parameters.

## Related Patterns

- [Comptroller Risk Gate](./pattern-comptroller-risk-gate.md)
- [Kinked Utilization Rate Model](./pattern-kinked-utilization-rate-model.md)
- [Correlated Collateral Basket](../../ANTIPATTERNS.md#correlated-collateral-basket)
