# Credit Loss Accounting Requirements

> Requirements for lending systems that can impair loans, realize bad debt, or carry unrealized credit losses.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, credit, impairment, bad-debt, losses |
| Type | Requirement |

## R1: Loss State Is Explicit

**A market must represent impaired, unrealized, and realized losses explicitly instead of relying on informal off-chain status.**

### What This Means

- Impaired principal and accrued interest are included in loss calculations.
- Bad debt is written into market totals, reserves, or an explicit loss bucket.
- If bad debt is assigned to a backstop before final default, backstop liabilities are tracked separately from borrower debt and terminal loss.
- Position status changes affect accounting, not only UI labels.

## R2: Losses Cannot Exceed Accounted Assets

**Loss calculations must be bounded so losses cannot underflow assets, exceed AUM except for documented rounding, or become negative during remediation.**

### What This Means

- Refinancing, repayment, impairment, and liquidation paths all recompute losses safely.
- Rounding direction is documented for partial recovery and write-off flows.
- Tests cover zero, dust, full-loss, and over-recovery cases.

## R3: Normal Issuance Respects Loss State

**Share issuance, redemption, interest distribution, and reported NAV must reflect active impairments and realized losses.**

### What This Means

- New entrants do not buy shares as if impaired assets were fully performing.
- Existing holders cannot exit at a price that ignores known losses.
- Interest stops, redirects, or is discounted according to the loan state.

## Verification Checklist

| Requirement | Question |
|-------------|----------|
| R1 | Are impairments and bad debt represented in on-chain accounting? |
| R2 | Can refinance, repayment, or liquidation make losses negative or exceed assets? |
| R3 | Do deposits, redemptions, and NAV reads include active loss state? |

## Source Evidence

- Maple tracks impaired principal and interest as unrealized losses, bounds losses against assets under management, and tests refinance/remediation cases that must avoid negative losses.
- Morpho Blue realizes uncovered liquidation debt only after collateral is exhausted, then reduces market totals so supplier loss is reflected immediately.
- Blend V2 demonstrates a backstop-assigned intermediate bad-debt state before thresholded terminal default.

## Related Patterns

- [Explicit Bad-Debt Realization](./pattern-explicit-bad-debt-realization.md)
- [Lending Accounting Freshness Requirements](./req-lending-accounting-freshness.md)
- [Toxic Liquidation Spiral](../../ANTIPATTERNS.md#toxic-liquidation-spiral)
