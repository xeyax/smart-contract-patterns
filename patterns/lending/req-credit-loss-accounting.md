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

## R4: Debt-Bearing Migration Preserves Loss State

**Moving collateral or account debt between pools, vaults, or markets must settle
current debt in the source context before assigning debt in the destination.**

### What This Means

- Current debt and accrued losses are consolidated before migration.
- The source assignment is cleared before destination assignment is written.
- Both source and destination vaults or pools are recalculated.
- The source is not left capacity-locked and the destination is not liquidatable
  immediately after migration.

## Verification Checklist

| Requirement | Question |
|-------------|----------|
| R1 | Are impairments and bad debt represented in on-chain accounting? |
| R2 | Can refinance, repayment, or liquidation make losses negative or exceed assets? |
| R3 | Do deposits, redemptions, and NAV reads include active loss state? |
| R4 | Does debt-bearing migration settle source debt and validate both sides before completion? |

## Source Evidence

- Maple tracks impaired principal and interest as unrealized losses, bounds losses against assets under management, and tests refinance/remediation cases that must avoid negative losses.
- Morpho Blue realizes uncovered liquidation debt only after collateral is exhausted, then reduces market totals so supplier loss is reflected immediately.
- Blend V2 demonstrates a backstop-assigned intermediate bad-debt state before thresholded terminal default.
- Gearbox V3 and Ajna provide explicit loss-waterfall evidence for
  treasury-first, reserve, bucket, and supplier loss realization in
  [`contracts/libraries/CreditLogic.sol:50-101`](https://github.com/gearbox-protocol/core-v3/blob/b038597d9070d9fd18593a6ae9c3d28ca931bb73/contracts/libraries/CreditLogic.sol#L50-L101)
  and [`src/libraries/external/SettlerActions.sol:85-201`](https://github.com/ajna-finance/ajna-core/blob/0f59e78031af76d62ad575c18405eb325b28849f/src/libraries/external/SettlerActions.sol#L85-L201).
- Synthetix V3 vault collateral migration settles current debt in the source
  pool, clears the old assignment, updates both positions, validates source and
  destination capacity/liquidation state, and assigns debt in the destination in
  [`protocol/synthetix/contracts/modules/core/VaultModule.sol:189-238`](https://github.com/synthetixio/synthetix-v3/blob/23585f73c76d625b2a43aaf94dc440a8a1e7a8fa/protocol/synthetix/contracts/modules/core/VaultModule.sol#L189-L238)
  and [`protocol/synthetix/contracts/modules/core/VaultModule.sol:374-435`](https://github.com/synthetixio/synthetix-v3/blob/23585f73c76d625b2a43aaf94dc440a8a1e7a8fa/protocol/synthetix/contracts/modules/core/VaultModule.sol#L374-L435).

## Related Patterns

- [Explicit Bad-Debt Realization](./pattern-explicit-bad-debt-realization.md)
- [Lending Accounting Freshness Requirements](./req-lending-accounting-freshness.md)
- [Toxic Liquidation Spiral](../../ANTIPATTERNS.md#toxic-liquidation-spiral)
