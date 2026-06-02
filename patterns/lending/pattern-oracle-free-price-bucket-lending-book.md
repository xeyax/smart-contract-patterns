# Oracle-Free Price-Bucket Lending Book

> Let lenders choose price buckets and derive borrow capacity from deposited quote liquidity instead of a protocol oracle.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, oracle-free, buckets, liquidation, price-discovery |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Lenders should explicitly price collateral risk through bucket deposits
- Borrow capacity can be derived from ordered liquidity rather than an oracle
- Liquidation and bad-debt settlement can walk price buckets deterministically
- The protocol can maintain bucket, loan, and liquidation priority structures

## Avoid When

- Users expect oracle-priced collateral factors and uniform LTVs
- Bucket rounding, bankruptcy, or deposit ordering cannot be explained to lenders
- Collateral tokens may be fee-on-transfer, rebasing, or otherwise unsupported
- Liquidation UX cannot tolerate bucket-specific settlement behavior

## How It Works

Lenders deposit quote tokens into indexed price buckets. The lending book derives
the lowest utilized price from bucket liquidity and checks borrowing against the
post-action book state:

```solidity
function borrow(uint256 amount, uint256 limitIndex) external {
    _addDebt(msg.sender, amount);
    uint256 lup = deposits.lowestUtilizedPrice(totalDebt);
    require(loanThresholdPrice(msg.sender) <= lup, "insufficient book liquidity");
    require(lupIndex() <= limitIndex, "price slipped");
}
```

Loans are ordered by risk, often through a heap keyed by threshold price, so the
riskiest loans can be kicked or settled without scanning every borrower.

## Key Points

- Treat "oracle-free" as lender-priced risk, not as absence of price risk.
- Compute borrow capacity from post-action bucket liquidity, not from stale
  pre-borrow liquidity.
- Maintain a bounded priority structure for the riskiest loans.
- Give borrowers a `limitIndex` or equivalent slippage bound because bucket
  deposits can move while a transaction is pending.
- Document unsupported token behavior such as fee-on-transfer and rebasing.
- Test bucket rounding, bankruptcy, auction settlement, and max-depth bad-debt
  forgiveness.

## Source Evidence

- Ajna documents oracle-free lender-priced lending and its unsupported token
  caveats in `/private/tmp/defillama-source/ajna-finance__ajna-core/README.md:1-27`.
- Ajna derives prices and indexes through bucket math in
  `/private/tmp/defillama-source/ajna-finance__ajna-core/src/libraries/helpers/PoolHelper.sol:22-95`
  and deposit-tree math in `/private/tmp/defillama-source/ajna-finance__ajna-core/src/libraries/internal/Deposits.sol:94-160`.
- Ajna checks borrower actions against post-action lending-book state in
  `/private/tmp/defillama-source/ajna-finance__ajna-core/src/libraries/external/BorrowerActions.sol:152-185`
  and lender bucket actions in `/private/tmp/defillama-source/ajna-finance__ajna-core/src/libraries/external/LenderActions.sol:152-209`.
- Ajna maintains risk-ordered loans through heap-backed loan storage in
  `/private/tmp/defillama-source/ajna-finance__ajna-core/src/libraries/internal/Loans.sol:21-29`
  and `/private/tmp/defillama-source/ajna-finance__ajna-core/src/libraries/internal/Loans.sol:73-110`.

## Related Patterns

- [Hint-Assisted Risk-Ordered Position List](./pattern-hint-assisted-risk-ordered-position-list.md)
- [Resettable Dutch Liquidation Auction](./pattern-resettable-dutch-liquidation-auction.md)
- [Explicit Bad-Debt Realization](./pattern-explicit-bad-debt-realization.md)
- [Reserve Exposure Caps](./pattern-reserve-exposure-caps.md)
