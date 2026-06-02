# Repayment Liveness Fallback Escrow

> Let borrowers repay and release collateral even when the lender cannot receive the repayment token directly, by escrowing lender proceeds.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, repayment, escrow, liveness, collateral |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Loan repayment sends funds to a lender, seller, or counterparty that may be blocked by token policy
- Borrower collateral release should not depend on the lender receiving tokens synchronously
- The protocol can custody exact lender proceeds in an escrow contract
- The payment token and escrow path are part of the supported integration surface

## Avoid When

- The protocol cannot distinguish lender-receive failure from payer-nonpayment
- Escrow accounting is not trusted or cannot support the payment token
- Repayment callbacks can re-enter loan state after collateral release
- Lender claims need off-chain dispute resolution rather than deterministic escrow

## Trade-offs

**Pros:**
- Preserves borrower repayment and collateral-release liveness
- Localizes denylist or receiver failures to lender claim flow
- Makes owed lender proceeds explicit after a failed direct transfer

**Cons:**
- Adds another custody and claim surface
- Requires careful ordering around loan state, collateral release, and callbacks
- Can hide unsupported-token assumptions if not tested per payment token

## How It Works

Repayment first computes the exact owed amount and updates loan accounting. The protocol then attempts to pay the lender directly. If the direct transfer fails because the lender cannot receive the token, the protocol pulls the same amount from the payer into protocol custody and deposits it into an escrow balance for the lender:

```solidity
function _payOrEscrow(uint256 loanId, address payer, address lender, uint256 amount) internal {
    bool paid = _tryTransferFrom(paymentToken, payer, lender, amount);
    if (!paid) {
        _safeTransferFrom(paymentToken, payer, address(this), amount);
        _approve(paymentToken, address(escrow), amount);
        escrow.deposit(lender, paymentToken, amount);
    }
}
```

Collateral release should depend on the borrower paying or escrowing the owed amount, not on the lender's address accepting the token in that transaction.

## Key Points

- Only fall back when lender receipt fails; payer transfer failures must still revert.
- Update loan state before external repayment callbacks, and make callbacks bounded or best-effort.
- Record escrow deposits by lender, token, and amount so claims are deterministic.
- Ensure fees, interest, and principal use the same liveness model or document the split.
- Test denylisted lenders, unsupported tokens, fee-on-transfer rejection, escrow claim, and callback failure.

## Source Evidence

- Teller V2 marks full repayment, removes the active bid, optionally withdraws collateral, then uses `_sendOrEscrowFunds` to either pay the lender or deposit lender proceeds into `EscrowVault` if direct payment fails in `/private/tmp/defillama-source/teller-protocol__teller-protocol-v2/packages/contracts/contracts/TellerV2.sol`.

## Real-World Examples

- Teller V2 - repayment can complete and collateral can be released even if lender token receipt fails.

## Related Patterns

- [Explicit Bad Debt Realization](./pattern-explicit-bad-debt-realization.md)
- [Balance Delta Transfer Accounting](../token-integration/pattern-balance-delta-transfer-accounting.md)
- [Withdrawal Liquidity Buffer](../vaults/pattern-withdrawal-liquidity-buffer.md)
