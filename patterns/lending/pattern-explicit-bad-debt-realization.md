# Explicit Bad-Debt Realization

> When liquidation cannot cover debt, reduce market supply and borrow totals immediately so insolvency is visible instead of hidden in stale accounting.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, liquidation, bad-debt, accounting, insolvency |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Liquidation can leave debt uncovered after seizing all collateral
- Suppliers or a reserve must absorb market-level losses
- The protocol uses share or index accounting that could otherwise hide insolvency
- Bad debt should not remain assigned to an empty borrower position

## Avoid When

- A separate insurance fund or auction guarantees full debt repayment before position closure
- Losses are intentionally deferred into a formal impairment accounting process
- The market cannot explain who absorbs the realized loss

## How It Works

After liquidating all collateral, compute any remaining debt and write it into market totals:

```solidity
if (repayAssets < borrowerDebt) {
    uint256 badDebt = borrowerDebt - repayAssets;
    totalBorrowAssets -= badDebt;
    totalSupplyAssets -= badDebt;
}

borrowShares[borrower] = 0;
collateral[borrower] = 0;
```

This makes the supplier haircut or reserve draw explicit in the market exchange rate.

### Backstop-Assigned Variant

Some markets assign a collateral-free borrower's liabilities to a backstop before
declaring terminal default:

```solidity
if (borrower.collateral == 0 && borrower.debt != 0) {
    backstopDebt += borrower.debt;
    borrower.debt = 0;
}

if (backstopCoverageBelowThreshold()) {
    realizeBackstopDefault(backstopDebt);
}
```

This delays the final supplier haircut while still making the absorbing party and
terminal default condition explicit.

## Key Points

- Accrue interest before liquidation and bad-debt calculation.
- Close the borrower's debt only after collateral seizure and repayment are accounted.
- Define whether reserves absorb loss before suppliers.
- If a backstop absorbs loss before suppliers, track backstop liabilities separately from terminal defaulted debt.
- Emit bad-debt events with market id and amount.
- Include invariants that no borrower has debt without collateral after terminal liquidation.

## Source Evidence

- Morpho Blue liquidations can wipe remaining debt and reduce total supply and borrow assets, with integration and formal checks around supplier haircut and no-debt-without-collateral invariants.
- Blend V2 assigns collateral-free user liabilities to the backstop and later defaults backstop liabilities only below a small-threshold condition in `/private/tmp/defillama-source/blend-capital__blend-contracts-v2/pool/src/pool/bad_debt.rs`, with tests for assignment and default.

## Related Patterns

- [Credit Loss Accounting Requirements](./req-credit-loss-accounting.md)
- [Share-Denominated Lending Accounting](./pattern-share-denominated-lending-accounting.md)
- [Toxic Liquidation Spiral](../../ANTIPATTERNS.md#toxic-liquidation-spiral)
