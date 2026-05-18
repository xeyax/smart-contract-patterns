# Comptroller Risk Gate

> Route market actions through a central risk module that approves borrows, redeems, transfers, and liquidations before state changes.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, comptroller, risk, collateral, liquidation |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A lending protocol has multiple collateral and borrow markets
- Account liquidity depends on cross-market collateral factors
- Markets should share pause, listing, and risk policies
- Liquidation eligibility must be checked consistently

## Avoid When

- The protocol has only one isolated market
- Risk checks are intentionally per-market and independent
- A central module would become an unbounded arbitrary execution surface

## How It Works

Each market calls the comptroller before changing balances:

```solidity
function borrow(uint256 amount) external {
    accrueInterest();
    require(comptroller.borrowAllowed(address(this), msg.sender, amount), "borrow denied");
    _borrowFresh(msg.sender, amount);
}

function redeem(uint256 shares) external {
    accrueInterest();
    require(comptroller.redeemAllowed(address(this), msg.sender, shares), "redeem denied");
    _redeemFresh(msg.sender, shares);
}
```

The comptroller computes hypothetical account liquidity after the requested action:

```solidity
liquidity = collateralValue(account) - borrowValue(account) - actionDelta;
require(liquidity >= 0, "insufficient liquidity");
```

## Key Points

- Run risk checks before effects but after local market freshness updates.
- Keep market-specific accounting in markets and cross-market policy in the comptroller.
- Make pause scopes explicit; pausing liquidations can extend bad-debt windows.
- Treat new market listing and collateral factor changes as high-risk governance actions.
- Avoid letting the comptroller execute arbitrary market calls.

## Source Evidence

- JustLend preflights borrow, redeem, transfer, and liquidation through comptroller hooks.
- Its comptroller sums hypothetical collateral and borrow effects across markets before allowing an action.

## Related Patterns

- [Lending Accounting Freshness Requirements](./req-lending-accounting-freshness.md)
- [Isolated Permissionless Market](./pattern-isolated-permissionless-market.md)
- [Toxic Liquidation Spiral](../../ANTIPATTERNS.md#toxic-liquidation-spiral)
