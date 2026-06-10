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

## Trade-offs

**Pros:**
- Cross-market account liquidity is computed in one place, so collateral rules cannot diverge between markets.
- Listing, pause, and collateral-factor policy changes apply consistently without touching market code.
- Hypothetical-liquidity preflight rejects unsafe actions before any balance changes, simplifying market-level invariants.
- Liquidation eligibility uses the same math as borrow/redeem checks, closing inconsistency exploits between paths.

**Cons:**
- Every borrow, redeem, transfer, and liquidation pays an extra cross-contract call plus a multi-market liquidity loop.
- The comptroller is a single point of failure: a policy bug or bad upgrade affects all markets at once.
- Cross-market liquidity math couples markets — a mispriced oracle or bad collateral factor in one market drains others.
- Governance over listings and collateral factors concentrates high-impact power that needs timelocks and monitoring.
- Pause scoping is delicate; pausing liquidations centrally can extend bad-debt windows across every market.

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
- Compound V2 routes `mintAllowed`, `redeemAllowed`, `borrowAllowed`, `liquidateBorrowAllowed`, and `seizeAllowed` through comptroller contracts in [`contracts/Comptroller.sol`](https://github.com/compound-finance/compound-protocol/blob/a3214f67b73310d547e00fc578e8355911c9d376/contracts/Comptroller.sol) and `ComptrollerG7.sol`.
- Compound tests pause-guardian behavior in [`tests/Comptroller/pauseGuardianTest.js`](https://github.com/compound-finance/compound-protocol/blob/a3214f67b73310d547e00fc578e8355911c9d376/tests/Comptroller/pauseGuardianTest.js).

## Related Patterns

- [Lending Accounting Freshness Requirements](./req-lending-accounting-freshness.md)
- [Isolated Permissionless Market](./pattern-isolated-permissionless-market.md)
- [Toxic Liquidation Spiral](../../ANTIPATTERNS.md#toxic-liquidation-spiral)
