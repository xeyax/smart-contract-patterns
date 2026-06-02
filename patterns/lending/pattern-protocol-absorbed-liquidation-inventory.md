# Protocol-Absorbed Liquidation Inventory

> Absorb underwater accounts into protocol reserves first, then sell seized collateral from protocol inventory under reserve and slippage constraints.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, liquidation, reserves, inventory, collateral-sale |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Liquidations should not require a liquidator to repay exact borrower debt in the same transaction
- The protocol can temporarily hold seized collateral inventory
- Reserve targets determine when collateral resale is needed
- Buyers should have explicit slippage protection on inventory sales

## Avoid When

- The protocol cannot safely custody seized collateral
- Reserve accounting cannot absorb borrower debt first
- Inventory sales would become an arbitrary treasury trading surface

## How It Works

Liquidation first absorbs borrower debt and collateral into protocol accounting:

```solidity
function absorb(address account) external {
    require(isLiquidatable(account), "healthy");
    reserves -= debt(account);
    protocolCollateral[asset] += collateral[account][asset];
    clearPosition(account);
}
```

The protocol later sells collateral inventory only when reserves are below target and the buyer supplies enough base asset:

```solidity
function buyCollateral(address asset, uint256 amount, uint256 maxCost) external {
    require(reserves < targetReserves, "reserves healthy");
    uint256 cost = quoteDiscountedCollateral(asset, amount);
    require(cost <= maxCost, "slippage");
    _sellInventory(asset, amount, cost);
}
```

## Key Points

- Separate account absorption from collateral resale.
- Clear borrower debt and collateral atomically during absorption.
- Cap sales by protocol-held inventory and reserve targets.
- Require buyer slippage bounds and asset allowlists.
- Emit events for bad debt, seized collateral, and inventory sales.

## Source Evidence

- Compound III absorbs underwater accounts into protocol reserves and later sells protocol-held collateral only under reserve and slippage constraints.

## Related Patterns

- [Explicit Bad-Debt Realization](./pattern-explicit-bad-debt-realization.md)
- [Resettable Dutch Liquidation Auction](./pattern-resettable-dutch-liquidation-auction.md)
- [Toxic Liquidation Spiral](../../ANTIPATTERNS.md#toxic-liquidation-spiral)
