# Upgrade-Slot Pinned Rate Adapter

> Pin an upgradeable upstream program's last upgrade slot and fail valuation until governance accepts the new slot.

## Metadata

| Property | Value |
|----------|-------|
| Category | oracles |
| Tags | oracle, solana, upgradeable-program, rate-adapter, liveness |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- A rate adapter reads state from an upgradeable upstream Solana program
- Upstream upgrade can change valuation semantics without changing account layout
- Governance or management can review and accept upstream upgrades
- Failing closed is safer than silently using changed semantics

## Avoid When

- The upstream program is immutable or already governed by the same upgrade boundary
- The adapter cannot read ProgramData metadata
- Valuation liveness is more important than detecting upstream semantic changes
- Governance cannot monitor and accept upgrades promptly

## How It Works

Store the accepted `last_upgrade_slot` for the upstream ProgramData account:

```rust
pub fn validate_program_data(program_data: &ProgramData, accepted_slot: u64) -> Result<()> {
    require!(program_data.last_upgrade_slot == accepted_slot, UpgradeSlotChanged);
    Ok(())
}

pub fn accept_upgrade(ctx: Context<AcceptUpgrade>) -> Result<()> {
    ctx.accounts.config.accepted_slot = ctx.accounts.program_data.last_upgrade_slot;
    Ok(())
}
```

If the upstream program upgrades, valuation fails until the manager accepts the new slot.

## Key Points

- Treat upgrade-slot pinning as a semantic-change circuit breaker, not market-price validation.
- Emit accepted-slot updates and monitor upstream ProgramData changes.
- Require authorized governance or manager signatures for slot acceptance.
- Document liveness impact when the upstream program upgrades.
- Test unauthorized slot updates, missing signatures, and stale accepted slots.

## Source Evidence

- Sanctum's Solana value calculators read upstream ProgramData, compare the last upgrade slot to a stored accepted slot, and test manager-controlled slot updates.

## Related Patterns

- [Exchange-Rate Valuation Risk](./risk-exchange-rate-valuation.md)
- [Read-Only Storage Resolver Facade](../monitoring/pattern-read-only-storage-resolver-facade.md)
