# Lazy Borrow Index

> Track global borrow interest with an index so borrower debt can be updated on demand instead of looping over all borrowers.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, borrow, interest, index, lazy-accounting |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- Borrow interest accrues continuously or per block
- The protocol has many borrowers
- Updating every borrower on every accrual would be impossible
- Borrow balances are needed only when a borrower interacts or risk is checked

## Avoid When

- Interest does not accrue over time
- Borrow positions are few enough for explicit accounting
- Rounding or index precision cannot be bounded

## How It Works

The market stores one global `borrowIndex`. Each borrower stores principal and the index at their last interaction.

```solidity
function borrowBalanceCurrent(address account) public returns (uint256) {
    accrueInterest();
    return borrowBalanceStored(account);
}

function borrowBalanceStored(address account) public view returns (uint256) {
    BorrowSnapshot memory b = accountBorrows[account];
    if (b.principal == 0) return 0;

    return b.principal * borrowIndex / b.interestIndex;
}
```

On borrow or repay, write the borrower's new principal and current index.

## Key Points

- Update the global index before value-changing actions.
- Store per-borrower snapshots as principal plus index, not continuously increasing debt.
- Define rounding direction consistently; tiny residual debt can become stuck.
- Include reserves in global accrual so accounting stays balanced.
- Pair with [Lending Accounting Freshness Requirements](./req-lending-accounting-freshness.md).
- If debt is represented by tokens, consider [Scaled Balance Token Accounting](./pattern-scaled-balance-token-accounting.md) so token balances derive from the same index.
- When a CDP also accrues protocol rewards, checkpoint debt interest and reward cursors before debt, collateral, liquidation, redemption, or claim paths mutate the position.
- For credit accounts with multiple debt components, define the repayment
  waterfall across principal, base interest, quota interest, quota fees, and
  protocol fees; partial repayment ordering and pro-rata fee splits must be
  explicit.
- If lenders accrue interest only when their bucket or deposit index is touched,
  document which actions refresh lender interest and which views are stale until
  interaction.

## Source Evidence

- JustLend computes borrower debt as principal multiplied by current borrow index divided by the borrower's stored interest index.
- Global borrow index, total borrows, and reserves update once per accrual.
- Compound V2 stores borrower debt as principal plus interest index and updates debt through `/private/tmp/defillama-source/compound-finance__compound-protocol/contracts/CToken.sol` functions `accrueInterest`, `borrowBalanceStored`, `borrowFresh`, `repayBorrowFresh`, and `liquidateBorrowFresh`.
- Compound tests borrow accrual, repayment, and liquidation freshness in `tests/Tokens/accrueInterestTest.js`, `borrowAndRepayTest.js`, and `liquidateTest.js`.
- Satoshi Core lazily applies trove debt interest and OSHI reward indexes around trove state changes in `/private/tmp/defillama-source/Satoshi-Protocol__satoshi-core/src/core/TroveManager.sol` and `src/logic/TroveManagerLogic.sol`.
- Zest Protocol stores user principal borrow balance plus the last variable-borrow index, then computes compounded borrow balances from reserve indexes in `/private/tmp/defillama-source/Zest-Protocol__zest-contracts/onchain/contracts/borrow/production/vaults/pool-0-reserve.clar`.
- Gearbox V3 defines multi-component credit-account debt and repayment ordering
  across principal, base interest, quota interest, quota fees, and protocol fees
  in `/private/tmp/defillama-source/gearbox-protocol__core-v3/contracts/libraries/CreditLogic.sol:132-154`,
  `/private/tmp/defillama-source/gearbox-protocol__core-v3/contracts/libraries/CreditLogic.sol:156-264`,
  and `/private/tmp/defillama-source/gearbox-protocol__core-v3/contracts/credit/CreditManagerV3.sol:385-470`.
- Ajna selectively updates lender interest through bucket/deposit interactions
  in `/private/tmp/defillama-source/ajna-finance__ajna-core/src/base/Pool.sol:537-578`
  and `/private/tmp/defillama-source/ajna-finance__ajna-core/src/libraries/external/PoolCommons.sol:249-289`.

## Related Patterns

- [Comptroller Risk Gate](./pattern-comptroller-risk-gate.md)
- [Kinked Utilization Rate Model](./pattern-kinked-utilization-rate-model.md)
- [Scaled Balance Token Accounting](./pattern-scaled-balance-token-accounting.md)
