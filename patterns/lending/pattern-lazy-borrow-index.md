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

## Source Evidence

- JustLend computes borrower debt as principal multiplied by current borrow index divided by the borrower's stored interest index.
- Global borrow index, total borrows, and reserves update once per accrual.
- Compound V2 stores borrower debt as principal plus interest index and updates debt through `/private/tmp/defillama-source/compound-finance__compound-protocol/contracts/CToken.sol` functions `accrueInterest`, `borrowBalanceStored`, `borrowFresh`, `repayBorrowFresh`, and `liquidateBorrowFresh`.
- Compound tests borrow accrual, repayment, and liquidation freshness in `tests/Tokens/accrueInterestTest.js`, `borrowAndRepayTest.js`, and `liquidateTest.js`.

## Related Patterns

- [Comptroller Risk Gate](./pattern-comptroller-risk-gate.md)
- [Kinked Utilization Rate Model](./pattern-kinked-utilization-rate-model.md)
- [Scaled Balance Token Accounting](./pattern-scaled-balance-token-accounting.md)
