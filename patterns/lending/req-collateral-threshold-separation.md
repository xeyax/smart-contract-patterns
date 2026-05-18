# Collateral Threshold Separation Requirements

> Requirements for lending markets that use different collateral factors for borrowing and liquidation.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, collateral-factor, liquidation, threshold |
| Type | Requirement |

## R1: Liquidation Threshold Exceeds Borrow Threshold

**The liquidation collateral factor must be strictly more permissive than the borrow collateral factor.**

### What This Means

- A position can move from borrowable to non-borrowable before becoming liquidatable.
- Rounding and precision downscaling must preserve the threshold gap.
- Listing tests reject equal or inverted thresholds.

## R2: Action Checks Use The Correct Threshold

**Borrow, redeem, and transfer checks use borrow collateral factors; liquidation checks use liquidation thresholds.**

### What This Means

- Oracle or collateral-value changes do not immediately liquidate accounts that only breached borrow capacity.
- Liquidation paths do not accidentally use the more permissive borrow check.
- Tests cover accounts between the two thresholds.

## R3: Freshness Scope Is Documented

**If some collateral-only actions rely on the threshold gap instead of accruing every market first, that scope must be explicit.**

### What This Means

- The design explains why the gap safely absorbs stale accounting windows.
- High-risk actions still accrue or fail closed where needed.
- Auditors can identify which views are stored and which are current.

## Source Evidence

- Compound III enforces liquidation collateral factors above borrow collateral factors and tests invalid threshold configurations.

## Related Patterns

- [Comptroller Risk Gate](./pattern-comptroller-risk-gate.md)
- [Single Borrow-Asset Market](./pattern-single-borrow-asset-market.md)
- [Lending Accounting Freshness Requirements](./req-lending-accounting-freshness.md)
