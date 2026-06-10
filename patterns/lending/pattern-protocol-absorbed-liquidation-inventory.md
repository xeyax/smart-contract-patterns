# Protocol-Absorbed Liquidation Inventory

> Absorb underwater accounts into protocol reserves first, then sell seized collateral from protocol inventory under reserve and slippage constraints.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, liquidation, reserve, inventory, collateral-sale |
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

## Trade-offs

**Pros:**
- Liquidators do not need to repay exact borrower debt atomically, lowering capital requirements and widening the liquidator set.
- Underwater accounts are cleared immediately on absorption, so borrower risk does not linger while collateral is sold.
- Reserve-target gating and buyer slippage bounds keep inventory sales constrained instead of becoming a discretionary trading surface.
- Decoupling absorption from resale lets collateral be sold when market conditions allow rather than at fire-sale moments.

**Cons:**
- The protocol takes price risk on held inventory between absorption and sale; collateral can decay further while reserves carry the debt.
- Reserves must be deep enough to absorb debt up front; thin reserves turn absorbed bad debt directly into supplier losses.
- Discount quoting for `buyCollateral` reintroduces oracle dependence and a mispricing surface on the resale path.
- Reserve accounting, protocol-held collateral balances, and per-asset allowlists add audit surface beyond a simple seize-and-transfer liquidation.
- Resale only triggers when reserves are below target, so inventory can sit idle and unhedged for long periods.

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
