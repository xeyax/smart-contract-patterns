# Solana Instruction-Paired Flash Loan

> On Solana, validate flash-loan borrow and repay instructions as a matched pair inside the same transaction.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | solana, flash-loan, instructions-sysvar, lending, atomicity |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | High |

## Use When

- A Solana lending program offers atomic flash loans
- The transaction can include both borrow and repay instructions
- The program can inspect the instructions sysvar
- CPI flash borrowing should be forbidden or tightly constrained

## Avoid When

- Flash loans should intentionally convert into open debt
- Repayment may happen in a later transaction
- The program cannot inspect or trust transaction instruction context

## Trade-offs

**Pros:**
- Avoids storing transient flash-loan debt state across transactions
- Detects missing, duplicated, or mismatched repay instructions before transfer
- Fits Solana's transaction-level atomicity model

**Cons:**
- Instruction parsing is brittle if account order or discriminators change
- CPI restrictions reduce composability
- The repay instruction still needs post-transfer accounting reconciliation

## How It Works

The borrow instruction inspects the transaction and requires a matching repay instruction later in the same transaction. The pair must match program id, discriminator, reserve, amount, fee receiver, and token accounts.

```rust
fn flash_borrow(ctx: Context<FlashBorrow>, amount: u64) -> Result<()> {
    let repay_ix = find_later_repay_instruction(&ctx.accounts.instructions, amount)?;
    validate_repay_accounts(repay_ix, &ctx.accounts)?;
    require_no_duplicate_flash_pair(&ctx.accounts.instructions)?;
    transfer_out(amount)
}
```

## Key Points

- Reject CPI borrow/repay unless the full caller model is audited.
- Require exactly one borrow/repay pair per reserve or transaction if multiple pairs cannot be safely distinguished.
- Match instruction discriminator, program id, reserve, amount, and token accounts.
- Recalculate and collect fees during repay.
- Reconcile vault balances after repayment, not only instruction presence.

## Source Evidence

- Kamino Lend flash-loan helpers inspect the instructions sysvar to validate matching borrow and repay instructions.
- Its flash validation rejects mismatched repay accounts and multiple or invalid flash instruction pairs.

## Related Patterns

- [Debt-Converting Flash Loan](./pattern-debt-converting-flash-loan.md)
- [PDA-Scoped Protocol Authority](../access-control/pattern-pda-scoped-protocol-authority.md)
- [Balance Delta Transfer Accounting](../token-integration/pattern-balance-delta-transfer-accounting.md)
