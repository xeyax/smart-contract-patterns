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

## Trade-offs

**Pros:**
- O(1) accrual regardless of borrower count — one global index update replaces an impossible loop over all positions.
- Per-borrower snapshots are touched only on interaction, keeping borrow/repay gas flat as the market grows.
- One index drives debt, reserves, and (with scaled tokens) balances, so all accounting derives from a single accrual source.
- Scales naturally to multi-component debt by layering additional cursors on the same lazy-checkpoint discipline.

**Cons:**
- Every value-changing path must accrue first; a single missed `accrueInterest` call reads stale debt into risk checks.
- Stored balances and views are stale between interactions, so off-chain consumers must know which reads accrue and which do not.
- Index-ratio rounding can strand residual dust debt or leak value if direction is inconsistent across borrow, repay, and liquidation.
- Long gaps between accruals compound rate error and stress index precision bounds.
- Multi-cursor extensions (rewards, quota interest, fee waterfalls) multiply checkpoint-ordering bugs — each mutation path must refresh every cursor in the right order.

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
- Compound V2 stores borrower debt as principal plus interest index and updates debt through [`contracts/CToken.sol`](https://github.com/compound-finance/compound-protocol/blob/a3214f67b73310d547e00fc578e8355911c9d376/contracts/CToken.sol) functions `accrueInterest`, `borrowBalanceStored`, `borrowFresh`, `repayBorrowFresh`, and `liquidateBorrowFresh`.
- Compound tests borrow accrual, repayment, and liquidation freshness in `tests/Tokens/accrueInterestTest.js`, `borrowAndRepayTest.js`, and `liquidateTest.js`.
- Satoshi Core lazily applies trove debt interest and OSHI reward indexes around trove state changes in [`src/core/TroveManager.sol`](https://github.com/Satoshi-Protocol/satoshi-core/blob/7f5eddaed965904fde10ea1d40c4c4b3ea118ada/src/core/TroveManager.sol) and `src/logic/TroveManagerLogic.sol`.
- Zest Protocol stores user principal borrow balance plus the last variable-borrow index, then computes compounded borrow balances from reserve indexes in [`onchain/contracts/borrow/production/vaults/pool-0-reserve.clar`](https://github.com/Zest-Protocol/zest-contracts/blob/3564bc38906e464ec4de774122bb9bbaee20ddc6/onchain/contracts/borrow/production/vaults/pool-0-reserve.clar).
- Gearbox V3 defines multi-component credit-account debt and repayment ordering
  across principal, base interest, quota interest, quota fees, and protocol fees
  in [`contracts/libraries/CreditLogic.sol:132-154`](https://github.com/gearbox-protocol/core-v3/blob/b038597d9070d9fd18593a6ae9c3d28ca931bb73/contracts/libraries/CreditLogic.sol#L132-L154),
  [`contracts/libraries/CreditLogic.sol:156-264`](https://github.com/gearbox-protocol/core-v3/blob/b038597d9070d9fd18593a6ae9c3d28ca931bb73/contracts/libraries/CreditLogic.sol#L156-L264),
  and [`contracts/credit/CreditManagerV3.sol:385-470`](https://github.com/gearbox-protocol/core-v3/blob/b038597d9070d9fd18593a6ae9c3d28ca931bb73/contracts/credit/CreditManagerV3.sol#L385-L470).
- Ajna selectively updates lender interest through bucket/deposit interactions
  in [`src/base/Pool.sol:537-578`](https://github.com/ajna-finance/ajna-core/blob/0f59e78031af76d62ad575c18405eb325b28849f/src/base/Pool.sol#L537-L578)
  and [`src/libraries/external/PoolCommons.sol:249-289`](https://github.com/ajna-finance/ajna-core/blob/0f59e78031af76d62ad575c18405eb325b28849f/src/libraries/external/PoolCommons.sol#L249-L289).

## Related Patterns

- [Comptroller Risk Gate](./pattern-comptroller-risk-gate.md)
- [Kinked Utilization Rate Model](./pattern-kinked-utilization-rate-model.md)
- [Scaled Balance Token Accounting](./pattern-scaled-balance-token-accounting.md)
