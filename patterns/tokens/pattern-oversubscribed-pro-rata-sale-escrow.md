# Oversubscribed Pro-Rata Sale Escrow

> Accept capped sale deposits into escrow, allocate tokens pro rata when demand exceeds supply, and refund unused payment plus fee overages.

## Metadata

| Property | Value |
|----------|-------|
| Category | tokens |
| Tags | token-sale, presale, escrow, pro-rata, refund |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A token sale may be oversubscribed
- Buyers deposit payment before the final allocation ratio is known
- Every buyer should receive a fair proportional fill rather than first-come priority
- Unused payment and excess fees must be claimable

## Avoid When

- The sale is strictly first-come-first-served
- The final sale supply or accepted payment total can be changed after claims start
- Refunds depend on a trusted operator without per-user accounting
- Rounding dust and fee refunds are not specified

## Trade-offs

**Pros:**
- Avoids gas races for fixed sale capacity
- Makes allocations deterministic after the sale closes
- Keeps refunds auditable per buyer

**Cons:**
- Buyers wait until finalization to know exact fill
- Claim math must handle rounding and fee overpayments
- Finalization state becomes a critical lifecycle boundary

## How It Works

During the deposit window, users escrow quote tokens and the sale records total committed quote. Once the sale is finalized, claim math computes each user's accepted quote, token allocation, refund, and fee refund from the global oversubscription ratio.

```rust
fn claim(ctx: Context) -> Result<()> {
    require!(sale.finalized, "not finalized");

    let accepted_quote = prorata(ctx.escrow.deposited, sale.max_quote, sale.total_quote);
    let token_out = accepted_quote * sale.token_supply / sale.max_quote;
    let refund = ctx.escrow.deposited - accepted_quote;
    let fee_refund = ctx.escrow.fee_paid - fee_for(accepted_quote);

    ctx.escrow.claimed = true;
    transfer_sale_tokens(ctx.buyer, token_out)?;
    refund_quote(ctx.buyer, refund + fee_refund)?;
}
```

## Implementation

### Key Points

- Freeze sale supply, accepted quote cap, and total committed quote before claims.
- Store per-user deposited quote and paid fee in escrow.
- Use one claim formula for token allocation, quote refund, and fee refund.
- Mark escrow claimed before transferring funds.
- Bound rounding direction and dust recovery explicitly.
- Test exact-fill, underfill, oversubscription, zero-fill dust, and repeated claims.

## Source Evidence

- Meteora Presale computes oversubscribed pro-rata claims in [`programs/presale/src/presale_mode_handler/prorata_presale.rs`](https://github.com/MeteoraAg/presale/blob/2acd7c9c20bada425e9ff493260be4328b350b57/programs/presale/src/presale_mode_handler/prorata_presale.rs) and `programs/presale/src/math/claim_math.rs`.
- Its sale state tracks deposit, claim, refund, and remaining-quote withdrawal behavior in `programs/presale/src/state/presale.rs`, with tests in `tests/test_withdraw_remaining_quote.rs`.

## Real-World Examples

- Meteora Presale allocates oversubscribed sale deposits pro rata and returns overflow quote plus fee refunds.

## Related Patterns

- [Merkle-Scoped Sale Escrow Caps](../access-control/pattern-merkle-scoped-sale-escrow-caps.md)
- [Async Deposit/Withdrawal](../vaults/pattern-async-deposit.md)
- [Operator-Finalized Withdrawal Claim](../vaults/pattern-operator-finalized-withdrawal-claim.md)

## References

- See Source Evidence.
