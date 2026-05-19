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
- Match the later repay instruction by explicit borrow-instruction index when the transaction can contain other lending instructions.
- Reject missing repay, mismatched reserve, mismatched amount, invalid repay index, duplicate flash borrow, and CPI borrow/repay paths in tests.
- Recalculate and collect fees during repay.
- Reconcile vault balances after repayment, not only instruction presence.

## Source Evidence

- Kamino Lend flash-loan helpers inspect the instructions sysvar to validate matching borrow and repay instructions.
- Its flash validation rejects mismatched repay accounts and multiple or invalid flash instruction pairs.
- Solend SPL Token Lending validates flash borrow and repay pairing in `/private/tmp/defillama-source/solendprotocol__solana-program-library/token-lending/program/src/processor.rs` through `_flash_borrow_reserve_liquidity` and `process_flash_repay_reserve_liquidity`.
- Solend tests invalid repay, missing repay, duplicate flash borrow, and CPI cases in `/private/tmp/defillama-source/solendprotocol__solana-program-library/token-lending/program/tests/flash_borrow_repay.rs`.

## Related Patterns

- [Debt-Converting Flash Loan](./pattern-debt-converting-flash-loan.md)
- [PDA-Scoped Protocol Authority](../access-control/pattern-pda-scoped-protocol-authority.md)
- [Balance Delta Transfer Accounting](../token-integration/pattern-balance-delta-transfer-accounting.md)
