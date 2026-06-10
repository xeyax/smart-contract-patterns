# Oracle-Free Price-Bucket Lending Book

> Let lenders choose price buckets and derive borrow capacity from deposited quote liquidity instead of a protocol oracle.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, oracle-free, bucket, liquidation, price-discovery |
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

## Trade-offs

**Pros:**
- Removes the protocol oracle as a manipulation and liveness dependency; lenders price collateral risk directly through bucket deposits.
- Permissionless market creation for any pair, since no oracle feed or governance-set collateral factor is required.
- Heap-keyed loan ordering lets the riskiest loans be kicked or settled without scanning every borrower.
- Borrow checks against post-action book state plus a `limitIndex` slippage bound protect borrowers from in-flight bucket movement.

**Cons:**
- Bucket math, deposit trees, loan heaps, and bucket bankruptcy form a large, hard-to-audit state machine; rounding bugs hide in index/price conversions.
- Borrow capacity depends on where lenders park liquidity, so available LTV is unpredictable compared to oracle-priced uniform collateral factors.
- Lender UX is demanding: depositors must understand bucket pricing, deposit ordering, and bucket-specific liquidation settlement or risk mispriced exposure.
- Fee-on-transfer and rebasing collateral are unsupported, narrowing the asset universe and requiring explicit onboarding documentation.
- Bad-debt settlement walks buckets and can forgive debt at max depth, so passive lenders in low buckets absorb losses they may not have modeled.

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
  caveats in [`README.md:1-27`](https://github.com/ajna-finance/ajna-core/blob/0f59e78031af76d62ad575c18405eb325b28849f/README.md#L1-L27).
- Ajna derives prices and indexes through bucket math in
  [`src/libraries/helpers/PoolHelper.sol:22-95`](https://github.com/ajna-finance/ajna-core/blob/0f59e78031af76d62ad575c18405eb325b28849f/src/libraries/helpers/PoolHelper.sol#L22-L95)
  and deposit-tree math in [`src/libraries/internal/Deposits.sol:94-160`](https://github.com/ajna-finance/ajna-core/blob/0f59e78031af76d62ad575c18405eb325b28849f/src/libraries/internal/Deposits.sol#L94-L160).
- Ajna checks borrower actions against post-action lending-book state in
  [`src/libraries/external/BorrowerActions.sol:152-185`](https://github.com/ajna-finance/ajna-core/blob/0f59e78031af76d62ad575c18405eb325b28849f/src/libraries/external/BorrowerActions.sol#L152-L185)
  and lender bucket actions in [`src/libraries/external/LenderActions.sol:152-209`](https://github.com/ajna-finance/ajna-core/blob/0f59e78031af76d62ad575c18405eb325b28849f/src/libraries/external/LenderActions.sol#L152-L209).
- Ajna maintains risk-ordered loans through heap-backed loan storage in
  [`src/libraries/internal/Loans.sol:21-29`](https://github.com/ajna-finance/ajna-core/blob/0f59e78031af76d62ad575c18405eb325b28849f/src/libraries/internal/Loans.sol#L21-L29)
  and [`src/libraries/internal/Loans.sol:73-110`](https://github.com/ajna-finance/ajna-core/blob/0f59e78031af76d62ad575c18405eb325b28849f/src/libraries/internal/Loans.sol#L73-L110).

## Related Patterns

- [Hint-Assisted Risk-Ordered Position List](./pattern-hint-assisted-risk-ordered-position-list.md)
- [Resettable Dutch Liquidation Auction](./pattern-resettable-dutch-liquidation-auction.md)
- [Explicit Bad-Debt Realization](./pattern-explicit-bad-debt-realization.md)
- [Reserve Exposure Caps](./pattern-reserve-exposure-caps.md)
