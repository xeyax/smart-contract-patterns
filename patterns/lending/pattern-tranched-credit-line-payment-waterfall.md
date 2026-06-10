# Tranched Credit-Line Payment Waterfall

> Route borrower repayments through a credit-line accounting waterfall that allocates senior and junior tranche principal, interest, fees, and losses.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, credit-line, tranche, waterfall, rwa |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A borrower draws against a credit line funded by senior and junior capital
- Pool tokens represent tranche positions and redeemable principal/interest
- Payments must allocate interest, principal, protocol fees, and junior incentives deterministically
- Junior capital is intended to absorb first-loss or receive separate economics

## Avoid When

- All lenders should share payments strictly pro rata
- Borrower repayment status is not tracked on-chain
- Admins can rewrite token principal or payment allocations without bounds
- Pool-token owners cannot independently redeem settled amounts

## Trade-offs

**Pros:**
- Makes credit-line repayment accounting explicit and auditable
- Supports different senior and junior economics
- Lets pool-token holders redeem settled amounts independently

**Cons:**
- Waterfall mistakes directly misallocate borrower payments
- Tranche-lock and redemption cursors increase state complexity
- Admin rewrite powers can undermine lender entitlement

## How It Works

Borrower payments enter the credit line and are split by waterfall rules before
updating per-tranche claim state:

```solidity
function pay(uint256 amount) external onlyBorrower {
    PaymentAllocation memory a = accountant.allocatePayment(creditLine, amount);
    creditLine.applyPayment(a);

    seniorTranche.principalPaid += a.seniorPrincipal;
    seniorTranche.interestPaid += a.seniorInterest;
    juniorTranche.principalPaid += a.juniorPrincipal;
    juniorTranche.interestPaid += a.juniorInterest;
    reserve += a.protocolFee;
}

function redeem(uint256 poolTokenId) external {
    Claim memory c = _claimable(poolTokenId);
    _advanceRedeemed(poolTokenId, c);
    _transfer(c.owner, c.amount);
}
```

## Implementation

### Key Points

- Lock tranche terms before borrower drawdown.
- Define payment priority for interest, principal, fees, reserve, and junior economics.
- Store per-token redeemed principal and interest cursors.
- Treat admin principal rewrites as exceptional trusted recovery, not normal accounting.
- Test partial payments, late payments, senior/junior splits, default/loss cases, and token redemption after transfers.

## Source Evidence

- Goldfinch tranched pool and drawdown logic are in [`packages/protocol/contracts/protocol/core/TranchedPool.sol`](https://github.com/goldfinch-eng/mono/blob/bb251675d8a28d046f4d4763e1cf8874ee7c2723/packages/protocol/contracts/protocol/core/TranchedPool.sol).
- Goldfinch credit-line payment and interest accounting are in [`packages/protocol/contracts/protocol/core/CreditLine.sol`](https://github.com/goldfinch-eng/mono/blob/bb251675d8a28d046f4d4763e1cf8874ee7c2723/packages/protocol/contracts/protocol/core/CreditLine.sol) and `Accountant.sol`.
- Goldfinch tranche allocation and redemption logic are in [`packages/protocol/contracts/protocol/core/TranchingLogic.sol`](https://github.com/goldfinch-eng/mono/blob/bb251675d8a28d046f4d4763e1cf8874ee7c2723/packages/protocol/contracts/protocol/core/TranchingLogic.sol).
- Goldfinch integration tests cover tranche drawdown and payment flows in [`packages/protocol/test/integration.test.ts`](https://github.com/goldfinch-eng/mono/blob/bb251675d8a28d046f4d4763e1cf8874ee7c2723/packages/protocol/test/integration.test.ts).

## Real-World Examples

- Goldfinch - borrower credit lines funded by senior and junior pool tranches.

## Related Patterns

- [Credit Loss Accounting Requirements](./req-credit-loss-accounting.md)
- [Explicit Bad Debt Realization](./pattern-explicit-bad-debt-realization.md)
- [Permissioned Exit Custody](../../ANTIPATTERNS.md#permissioned-exit-custody)

## References

- See Source Evidence.
