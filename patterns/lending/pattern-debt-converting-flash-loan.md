# Debt-Converting Flash Loan

> Allow unpaid flash-loan principal to become normal borrow debt only after the same risk, fee, callback, and accounting checks as an ordinary borrow.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, flash-loan, debt, callback, borrow |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Flash borrowers should be able to keep part of the borrowed amount as debt
- The protocol can run ordinary borrow risk checks during flash-loan settlement
- Fees are charged on the flash-loan amount regardless of repayment mix
- The market can account for active flash-loan cash during exchange-rate reads

## Avoid When

- Flash loans must be fully repaid atomically by design
- Borrow risk checks cannot run safely after the callback
- The callback target or delegate can bypass authorization
- The market cannot distinguish active flash-loan amounts from free cash

## How It Works

After callback, repay what was returned and convert the unpaid amount into debt:

```solidity
function settleFlashLoan(address borrower, uint256 amount, uint256 repaid) internal {
    uint256 fee = _flashFee(amount);
    require(repaid >= fee, "fee not paid");

    uint256 unpaidPrincipal = amount - min(repaid - fee, amount);
    if (unpaidPrincipal > 0) {
        _borrowFresh(borrower, unpaidPrincipal);
    }
}
```

The debt conversion path should be indistinguishable from a normal borrow for collateral, pause, oracle, and accrual checks.

## Key Points

- Accrue the market before creating debt.
- Verify callback authorization, asset list, delegate, and receiver.
- Enforce a fee floor even when principal converts to debt.
- Cap repayment accounting so overpayment cannot create negative debt.
- Include active flash-loan amounts in exchange-rate cash logic.
- If debt is opened on behalf of another account, consume borrow delegation or credit allowance during settlement.
- Test full repay, partial repay, fee-only repay, failed risk checks, and reentrancy.

## Source Evidence

- Venus flash loans allow unpaid balances to become borrower debt through the normal borrow path, with market, delegate, fee, repayment, and accounting checks.
- Aave V2 flash loans require repayment plus premium for mode `NONE`, while nonzero modes route post-callback unpaid principal through ordinary borrow validation and stable or variable debt minting in `/private/tmp/defillama-source/aave__protocol-v2/contracts/protocol/lendingpool/LendingPool.sol`; tests cover variable debt conversion and delegated stable debt.

## Related Patterns

- [Comptroller Risk Gate](./pattern-comptroller-risk-gate.md)
- [Lazy Borrow Index](./pattern-lazy-borrow-index.md)
- [Nontransferable Debt Token Delegation](./pattern-nontransferable-debt-token-delegation.md)
- [Hook/Callback Trust](../../ANTIPATTERNS.md#hookcallback-trust)
