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

### Full-Account Dust Healing Variant

Some lending systems route accounts below a minimum debt or collateral threshold away from ordinary close-factor liquidation into full-account liquidation or healing:

```solidity
if (_belowDustThreshold(account)) {
    _liquidateOrHealEntireAccount(account);
} else {
    _ordinaryCloseFactorLiquidation(account);
}
```

This prevents tiny remnants from surviving repeated partial liquidations. If the full-account path realizes protocol loss, pair it with explicit bad-debt accounting.

## Key Points

- Cap both global and per-asset in-flight liquidation exposure where needed.
- Define dust in terms of debt, collateral, auction lot size, and keeper economics.
- Make cap increases governance-controlled and monitored.
- Ensure cap exhaustion does not permanently block liquidation progress.
- Test full, partial, cap-full, dust-remainder, and null-auction cases.
- Route below-threshold accounts through a full-account or bad-debt-healing path rather than leaving uneconomic remnants.
- If a liquidation hook chooses between partial and full-account liquidation, keep the dust threshold, close factor, and collateral priority in one audited path.

## Source Evidence

- Sky/Maker DSS liquidation modules bound global and per-collateral active liquidation debt and reject partial liquidations that would create dusty remnants or invalid auctions.
- Girin/Doppler-style comptroller code routes below-threshold accounts away from ordinary close-factor liquidation into full-account liquidation or healing.
- Silo V2 partial-liquidation hooks implement collateral priority and close-factor behavior in `/private/tmp/defillama-source/silo-finance__silo-contracts-v2/silo-core/contracts/hooks/liquidation/lib/PartialLiquidationLib.sol`.
- Term Finance liquidation contracts and auction specs cover fixed-maturity repo liquidation flows under `/private/tmp/defillama-source/term-finance__term-finance-contracts/contracts` and `/private/tmp/defillama-source/term-finance__term-finance-contracts/certora/specs`.

## Related Patterns

- [Reserve Exposure Caps](./pattern-reserve-exposure-caps.md)
- [Resettable Dutch Liquidation Auction](./pattern-resettable-dutch-liquidation-auction.md)
- [Explicit Bad Debt Realization](./pattern-explicit-bad-debt-realization.md)
- [Toxic Liquidation Spiral](../../ANTIPATTERNS.md#toxic-liquidation-spiral)
