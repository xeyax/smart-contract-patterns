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

## Trade-offs

**Pros:**
- In-flight caps match liquidation throughput to auction and keeper capacity, preventing market-crushing collateral dumps.
- Dust rejection guarantees every surviving position and auction lot stays economically resolvable.
- Full-account routing for below-threshold positions stops tiny remnants from surviving repeated partial liquidations.
- Per-asset caps contain a single collateral's stress event from consuming global liquidation capacity.

**Cons:**
- Cap exhaustion delays liquidation of underwater positions, widening the bad-debt window exactly when speed matters most.
- Dust thresholds and caps are calibration-sensitive governance parameters; stale values either block keepers or readmit uneconomic remnants.
- "Cap full" and "dust remainder" reverts complicate keeper bots, which must size liquidations against live cap room.
- The decision tree (full vs partial vs heal, cap room, dust check) concentrates several failure cases in one path that all need tests.
- Full-account healing can realize protocol loss, so it drags in bad-debt accounting as a hard dependency.

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
- Silo V2 partial-liquidation hooks implement collateral priority and close-factor behavior in [`silo-core/contracts/hooks/liquidation/lib/PartialLiquidationLib.sol`](https://github.com/silo-finance/silo-contracts-v2/blob/fd1c73beafb7c81f77cd4477002ebadb4142d243/silo-core/contracts/hooks/liquidation/lib/PartialLiquidationLib.sol).
- Term Finance liquidation contracts and auction specs cover fixed-maturity repo liquidation flows under [`contracts`](https://github.com/term-finance/term-finance-contracts/blob/262098c71578bbb9e54d6c2a8d2d88d112b9662a/contracts) and [`certora/specs`](https://github.com/term-finance/term-finance-contracts/blob/262098c71578bbb9e54d6c2a8d2d88d112b9662a/certora/specs).

## Related Patterns

- [Reserve Exposure Caps](./pattern-reserve-exposure-caps.md)
- [Resettable Dutch Liquidation Auction](./pattern-resettable-dutch-liquidation-auction.md)
- [Explicit Bad Debt Realization](./pattern-explicit-bad-debt-realization.md)
- [Toxic Liquidation Spiral](../../ANTIPATTERNS.md#toxic-liquidation-spiral)
