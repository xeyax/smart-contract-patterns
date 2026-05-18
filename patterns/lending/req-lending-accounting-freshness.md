# Lending Accounting Freshness Requirements

> Requirements for lending markets whose interest, exchange rates, and risk checks update lazily.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, interest, freshness, accrual, accounting |
| Type | Requirement |

## R1: Accrue Before Value-Changing Actions

**A market must bring interest and reserves current before mint, borrow, redeem, repay, or liquidation changes state.**

```
accrualBlock == block.number
```

### What This Means

- Exchange rates use current interest.
- Borrow balances reflect the latest global borrow index.
- Reserves and total borrows are updated before user-visible accounting changes.

## R2: Freshness Scope Is Explicit

**The protocol documents which checks use freshly accrued state and which use stored snapshots.**

### What This Means

- Single-market actions can require same-block accrual.
- Cross-market liquidity may intentionally use stored balances for gas reasons.
- Audits and tests must distinguish local market freshness from account-wide risk freshness.

## R3: Stale Actions Fail Closed

**If accrual fails, value-changing actions revert instead of proceeding with stale state.**

### What This Means

- Interest model errors block the action.
- Oracle failures in exchange-rate or liquidity checks block the action.
- Liquidations do not use stale collateral or debt accounting.

## Verification Checklist

| Requirement | Question |
|-------------|----------|
| R1 | Does every mint/borrow/redeem/repay/liquidate path accrue first? |
| R2 | Are stored snapshot reads clearly documented? |
| R3 | Can stale accrual be bypassed through a secondary entry point? |

## Source Evidence

- JustLend accrues interest before mint, borrow, redeem, and liquidation paths and checks same-block freshness before state transitions.
- Its comptroller liquidity checks use stored snapshots for cross-market calculations, showing why freshness scope must be explicit.

## Related Patterns

- [Lazy Borrow Index](./pattern-lazy-borrow-index.md)
- [Comptroller Risk Gate](./pattern-comptroller-risk-gate.md)
