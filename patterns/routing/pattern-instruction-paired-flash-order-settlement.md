# Instruction-Paired Flash Order Settlement

> Settle a routed order across a start/end instruction pair by locking order state, measuring output balance deltas, and validating the paired end instruction before releasing maker inventory.

## Metadata

| Property | Value |
|----------|-------|
| Category | routing |
| Tags | routing, orderbook, flash, solana, balance-delta |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Makers post on-chain inventory but takers need to route through arbitrary swap legs before final settlement
- The chain exposes transaction instruction introspection, such as Solana's instructions sysvar
- Settlement can lock an order for one transaction and unlock it only after measured balance-delta payment
- User protection depends on minimum output and exact account matching, not a trusted off-chain quote

## Avoid When

- The platform cannot prove the start and end instructions are in the same transaction
- Interstitial instructions can invoke the order program or mutate locked order state
- Output accounting relies on quoted amounts instead of token-account balance deltas
- Token extensions or transfer hooks are supported without validating all required remaining accounts

## Trade-offs

**Pros:**
- Lets takers source liquidity through flexible routes while makers keep custody in program-owned vaults
- Converts complex route correctness into a measured output delta at settlement
- Prevents a start instruction from leaving an order locked across transactions

**Cons:**
- Requires instruction introspection and careful CPI restrictions
- The account list and argument matching surface is large
- Token-extension support can expand the remaining-account validation boundary

## How It Works

The start instruction locks the order, records the taker's output-token balance, and validates that the matching end instruction appears later in the same transaction. The taker can then execute allowed swap or transfer legs. The end instruction revalidates the start arguments and accounts, computes the output balance delta, enforces the maker's minimum output, pays the maker pro rata, and unlocks or updates the order.

```rust
fn flash_take_order_start(ctx: Context<Start>, args: TakeArgs) -> Result<()> {
    require_matching_end_instruction(&ctx, &args)?;
    require!(!ctx.accounts.order.locked, OrderLocked);

    ctx.accounts.order.locked = true;
    ctx.accounts.order.start_output_balance = ctx.accounts.taker_output.amount;
    Ok(())
}

fn flash_take_order_end(ctx: Context<End>, args: TakeArgs) -> Result<()> {
    require_matching_start_instruction(&ctx, &args)?;

    let received = ctx.accounts.taker_output.amount
        .checked_sub(ctx.accounts.order.start_output_balance)?;
    require!(received >= args.min_output_amount, Slippage);

    pay_maker_from_delta(received)?;
    update_or_close_order()?;
    ctx.accounts.order.locked = false;
    Ok(())
}
```

The route between start and end is intentionally flexible, but the settlement boundary is not: the end instruction must see the same order, maker, taker, mints, amounts, and token accounts that the start instruction committed to.

## Key Points

- Validate the paired end instruction before locking the order.
- Block interstitial calls that can re-enter the order program or mutate the same order.
- Bind all value-bearing arguments and accounts across the start and end instructions.
- Measure taker output by token-account balance delta and enforce `min_output_amount`.
- Use ceiling or maker-favorable rounding when converting partial fills into maker proceeds.
- Unlock the order on every successful end path and test failed starts, mismatched ends, and replayed pairs.
- Treat Token-2022 hooks, transfer fees, or withheld amounts as separate validation boundaries.

## Source Evidence

- Kamino Limo stores order lock state and flash-take balance snapshots in `/private/tmp/defillama-source/Kamino-Finance_limo/programs/limo/src/state.rs`.
- Kamino Limo validates order settlement deltas, maker payouts, and order updates in `/private/tmp/defillama-source/Kamino-Finance_limo/programs/limo/src/operations.rs`.
- Kamino Limo's flash take handlers pair start/end instructions, validate route boundaries, and settle measured output in `/private/tmp/defillama-source/Kamino-Finance_limo/programs/limo/src/handlers/flash_take_order.rs`.
- Kamino Limo's instruction parser checks paired instruction placement and interstitial restrictions in `/private/tmp/defillama-source/Kamino-Finance_limo/programs/limo/src/utils/flash_ixs.rs`.

## Related Patterns

- [Solana Instruction-Paired Flash Loan](../lending/pattern-solana-instruction-paired-flash-loan.md)
- [Balance-Delta Transfer Accounting](../token-integration/pattern-balance-delta-transfer-accounting.md)
- [Typed Signed Order Settlement](./pattern-typed-signed-order-settlement.md)
- [Missing Slippage Protection](../../ANTIPATTERNS.md#missing-slippage-protection)
- [Quote Execution Formula Drift](../../ANTIPATTERNS.md#quote-execution-formula-drift)
