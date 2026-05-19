# Instruction-Paired Rebalance Solvency Record

> Bracket an external rebalance with start/end instructions that lock the pool, record pre-rebalance value, and reject completion unless solvency is preserved.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | liquidity, rebalance, solana, lst, solvency |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A pool must route inventory through external programs to rebalance reserves
- The protocol can inspect transaction instructions and require a paired end instruction
- Pool value can be measured before and after through conservative calculators
- User-facing routes and administrative rebalances share liquidity that must not lose value

## Avoid When

- The rebalance cannot be completed atomically or safely locked
- The end instruction cannot resync affected reserves before comparing value
- External routes lack slippage bounds or use quote formulas known to drift
- Rebalance locks would block exits without an emergency recovery path

## Trade-offs

**Pros:**
- Allows flexible external routing while keeping the pool's solvency invariant on-chain
- Makes rebalances auditable through a short-lived record account
- Prevents concurrent swaps or deposits from observing half-rebalanced state

**Cons:**
- Depends on instruction introspection and strict account matching
- Can halt pool operations if a lock or record is not cleared correctly
- Exact-in and exact-out quote semantics need separate tests to avoid route-level slippage gaps

## How It Works

The start instruction verifies that a matching end instruction appears later in the transaction, locks the pool or affected reserves, records the old total value and input reserve, and transfers the output inventory to the route. After the external route finishes, the end instruction resyncs the input reserve, recomputes total value, rejects value loss, and clears the lock.

```rust
fn start_rebalance(ctx: Context<StartRebalance>, args: RebalanceArgs) -> Result<()> {
    require_matching_end_instruction(&ctx, &args)?;

    ctx.accounts.pool.rebalancing = true;
    ctx.accounts.record.old_total_value = sync_total_value(&ctx.accounts.pool)?;
    ctx.accounts.record.input_lst_index = args.input_lst_index;
    transfer_output_inventory_to_route()?;
    Ok(())
}

fn end_rebalance(ctx: Context<EndRebalance>, args: RebalanceArgs) -> Result<()> {
    sync_input_reserve(args.input_lst_index)?;
    let new_total_value = sync_total_value(&ctx.accounts.pool)?;
    require!(new_total_value >= ctx.accounts.record.old_total_value, PoolValueDecreased);

    ctx.accounts.pool.rebalancing = false;
    close_record()?;
    Ok(())
}
```

## Key Points

- Validate the paired end instruction before transferring inventory out.
- Lock the pool or affected reserve set while the rebalance is in progress.
- Store the pre-rebalance total value and affected reserve identity in a short-lived record.
- Resync affected reserves before comparing post-rebalance value.
- Reject completion if total value decreases under the configured conservative calculators.
- Keep user slippage and route quote checks separate from protocol value preservation.
- Test mismatched pairs, missing end instructions, stale calculator data, value decrease, and lock clearing.

## Source Evidence

- Sanctum INF starts rebalances by checking paired instructions, locking the pool, recording old value, and transferring output inventory in `/private/tmp/defillama-source/igneous-labs_inf-1.5/controller/program/src/instructions/rebalance/start.rs`.
- Sanctum INF stores rebalance record state in `/private/tmp/defillama-source/igneous-labs_inf-1.5/controller/core/src/accounts/rebalance_record.rs`.
- Sanctum INF ends rebalances by syncing reserves, comparing new total value with the recorded value, and clearing the lock in `/private/tmp/defillama-source/igneous-labs_inf-1.5/controller/program/src/instructions/rebalance/end.rs`.
- Sanctum INF tests paired rebalance chains and value-preservation behavior in `/private/tmp/defillama-source/igneous-labs_inf-1.5/controller/program/tests/tests/rebalance/chain.rs`.

## Related Patterns

- [Conservative LST Router Value Preservation](./pattern-conservative-lst-router-value-preservation.md)
- [Invariant-Delta Liquidity Accounting](./pattern-invariant-delta-liquidity-accounting.md)
- [Verified Callback Settlement](./pattern-verified-callback-settlement.md)
- [Balance-Delta Transfer Accounting](../token-integration/pattern-balance-delta-transfer-accounting.md)
- [Missing Slippage Protection](../../ANTIPATTERNS.md#missing-slippage-protection)
