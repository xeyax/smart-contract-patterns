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

## R4: Risk Reductions Preserve Exit Windows

**When collateral support is reduced, new borrowing can be disabled immediately while liquidation thresholds ramp down over time.**

### What This Means

- Borrow thresholds can move to the safer value immediately to stop new debt.
- Liquidation thresholds can ramp only downward so existing borrowers have an orderly exit window.
- Upward or equal-risk threshold changes should not use the ramp path.
- Equality between borrow and liquidation thresholds is a no-grace-buffer mode, not the recommended default.

## R5: Liquidation Bonus Does Not Invert Collateral Safety

**Liquidation incentive and threshold settings must not let liquidators seize more value than the threshold model can support.**

### What This Means

- Liquidation bonus is above par but bounded.
- Threshold multiplied by liquidation bonus stays within full collateral value.
- Equal borrow and liquidation thresholds, if permitted, are treated as no-grace-buffer mode rather than the safe default.

## Source Evidence

- Compound III enforces liquidation collateral factors above borrow collateral factors and tests invalid threshold configurations.
- Euler V2 applies borrow LTV changes immediately while optionally ramping only lower liquidation LTVs over time, and tests both immediate borrow disablement and delayed liquidation eligibility.
- Aave V2 enforces non-inverted collateral configuration and liquidation-bonus bounds, including `threshold * bonus <= 100%`, in `/private/tmp/defillama-source/aave__protocol-v2/contracts/protocol/lendingpool/LendingPoolConfigurator.sol`; this supports bonus calibration but does not weaken the stricter threshold-gap recommendation.

## Related Patterns

- [Comptroller Risk Gate](./pattern-comptroller-risk-gate.md)
- [Single Borrow-Asset Market](./pattern-single-borrow-asset-market.md)
- [Lending Accounting Freshness Requirements](./req-lending-accounting-freshness.md)
