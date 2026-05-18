# Dust-Aware Liquidation Cap

> Bound in-flight liquidation debt and fail partial liquidations that would leave uneconomic dust positions or null auctions.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, liquidation, dust, auction, cap |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Liquidations create auctions or protocol inventory that has operational capacity
- Global or per-market liquidation throughput should be capped
- Partial liquidations are needed when caps are nearly full
- Tiny residual debt or collateral would be uneconomic to resolve

## Avoid When

- Liquidations always repay full debt atomically with no external auction or inventory
- Dust thresholds cannot be calibrated
- Caps can block all bad-debt containment during stress

## How It Works

Track active liquidation debt and limit new liquidation work:

```solidity
uint256 room = maxActiveLiquidationDebt - activeLiquidationDebt;
uint256 debtToLiquidate = min(positionDebt, room);
require(debtToLiquidate > 0, "cap full");
require(!_leavesDust(positionDebt - debtToLiquidate), "dust remainder");
```

If a partial liquidation would leave a dust position or create an auction too small to clear, fail closed or require a full liquidation after capacity is freed.

## Key Points

- Cap both global and per-asset in-flight liquidation exposure where needed.
- Define dust in terms of debt, collateral, auction lot size, and keeper economics.
- Make cap increases governance-controlled and monitored.
- Ensure cap exhaustion does not permanently block liquidation progress.
- Test full, partial, cap-full, dust-remainder, and null-auction cases.

## Source Evidence

- Sky/Maker DSS liquidation modules bound global and per-collateral active liquidation debt and reject partial liquidations that would create dusty remnants or invalid auctions.

## Related Patterns

- [Reserve Exposure Caps](./pattern-reserve-exposure-caps.md)
- [Resettable Dutch Liquidation Auction](./pattern-resettable-dutch-liquidation-auction.md)
- [Toxic Liquidation Spiral](../../ANTIPATTERNS.md#toxic-liquidation-spiral)
