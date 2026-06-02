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

### Same-Distribution Write-Off Variant

Reward or fee distributions can discover uncollectible debt after the debt set
has been configured. If pushing the loss into a future distribution would distort
current rewards, write the bad debt into the same distribution before sweep:

```solidity
if (debtFinalized && writeOffEnabled && !debtProcessed[index]) {
    processedDebt[index] = true;
    processedWriteOff[index] = true;
    uncollectibleDebt += debtAmount;
}
```

This is not a liquidation haircut, but the accounting rule is the same: make the
absorbing distribution explicit instead of hiding the loss in a later period.

### Treasury-First And Bucket-Bankruptcy Variants

Markets can define an ordered loss waterfall before suppliers are diluted. A
credit pool can burn treasury LP shares first, emit uncovered loss, zero risky
quota limits, and freeze new borrowing after a bad-debt liquidation. A
price-bucket lending book can absorb bad debt through high-price bucket deposits,
then reserves, then bounded bucket bankruptcy or debt forgiveness.

## Key Points

- Accrue interest before liquidation and bad-debt calculation.
- Close the borrower's debt only after collateral seizure and repayment are accounted.
- Define whether reserves absorb loss before suppliers.
- If a backstop absorbs loss before suppliers, track backstop liabilities separately from terminal defaulted debt.
- If debt is tied to a reward distribution, finalize the debt set before allowing write-offs and prevent sweep until write-off windows are closed.
- Make the loss waterfall explicit: treasury shares, reserves, bucket deposits,
  backstop, and suppliers should be ordered in code, events, and invariants.
- If a liquidation loss invalidates a quota or credit line, zero or freeze that
  exposure before allowing new borrowing.
- Emit bad-debt events with market id and amount.
- Include invariants that no borrower has debt without collateral after terminal liquidation.

## Source Evidence

- Morpho Blue liquidations realize remaining debt only after all collateral is gone, then reduce total borrow and total supply assets, with integration and formal checks around supplier haircut and no-debt-without-collateral invariants.
- Blend V2 assigns collateral-free user liabilities to the backstop and later defaults backstop liabilities only below a small-threshold condition in `/private/tmp/defillama-source/blend-capital__blend-contracts-v2/pool/src/pool/bad_debt.rs`, with tests for assignment and default.
- Fraxlend realizes bad debt during liquidation by reducing both `totalBorrow.amount` and `totalAsset.amount` when collateral cannot cover debt in `/private/tmp/defillama-source/FraxFinance__fraxlend/src/contracts/FraxlendPairCore.sol`.
- DoubleZero Solana supports same-distribution Solana validator debt write-offs after debt finalization and records processed debt and write-off bitmaps in `/private/tmp/defillama-source/doublezerofoundation__doublezero-solana/programs/revenue-distribution/src/processor.rs`, with tests in `tests/write_off_solana_validator_debt_test.rs`.
- Gearbox V3 liquidation loss burns treasury LP shares before supplier dilution,
  emits uncovered loss, zeros risky quota limits, and can freeze new borrowing
  after bad debt in `/private/tmp/defillama-source/gearbox-protocol__core-v3/contracts/libraries/CreditLogic.sol:50-101`,
  `/private/tmp/defillama-source/gearbox-protocol__core-v3/contracts/credit/CreditManagerV3.sol:291-374`,
  and `/private/tmp/defillama-source/gearbox-protocol__core-v3/contracts/pool/PoolV3.sol:471-524`.
- Ajna settles bad debt through ordered bucket deposits, reserves, and bounded
  bucket bankruptcy/debt forgiveness in `/private/tmp/defillama-source/ajna-finance__ajna-core/src/libraries/external/SettlerActions.sol:85-201`,
  `/private/tmp/defillama-source/ajna-finance__ajna-core/src/libraries/external/SettlerActions.sol:347-440`,
  and `/private/tmp/defillama-source/ajna-finance__ajna-core/tests/INVARIANTS.md:67-80`.

## Related Patterns

- [Credit Loss Accounting Requirements](./req-credit-loss-accounting.md)
- [Share-Denominated Lending Accounting](./pattern-share-denominated-lending-accounting.md)
- [Toxic Liquidation Spiral](../../ANTIPATTERNS.md#toxic-liquidation-spiral)
