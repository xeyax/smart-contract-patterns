# Bonding-Curve Terminal Liquidity Cutover

> Migrate a completed bonding curve into an AMM pool by computing the terminal price, seeding liquidity, collecting protocol fees, and marking the curve migrated atomically.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | bonding-curve, launchpad, migration, amm, liquidity |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A launch token trades on a bonding curve before graduating to AMM liquidity
- The final curve state should determine AMM starting price and inventory
- Protocol or migration fees must be accounted before surplus is burned or swept
- Migration should be one-way and visible to routers

## Avoid When

- The curve can continue trading after AMM migration
- The AMM configuration or starting price is selected off-chain without validation
- Surplus token handling is undefined
- Users need a reversible migration path

## Trade-offs

**Pros:**
- Creates a deterministic handoff from launch discovery to AMM trading
- Avoids leaving curve inventory and AMM inventory inconsistent
- Makes migration fees and surplus burns auditable

**Cons:**
- Migration math is sensitive to decimals, virtual reserves, and AMM price format
- One faulty migration can permanently seed the AMM at a bad price
- Requires tests across terminal curve edge cases

## How It Works

The migration handler reads the terminal bonding-curve state, computes the AMM starting price and liquidity amounts, validates the destination pool configuration, deposits the seed liquidity, extracts protocol or partner fees, burns or escrows surplus, and marks the launch pool migrated.

```rust
fn migrate_curve(ctx: Context) -> Result<()> {
    require!(curve.is_terminal(), "not complete");
    require!(!curve.migrated, "migrated");

    let price = curve.terminal_price()?;
    let seed = compute_seed_liquidity(curve.reserves, price, migration_fee)?;
    validate_amm_config(ctx.amm_config, seed)?;

    deposit_initial_liquidity(ctx.amm_pool, seed.base, seed.quote)?;
    collect_protocol_fee(seed.protocol_fee)?;
    burn_surplus(curve.surplus_tokens)?;

    curve.migrated = true;
}
```

## Implementation

### Key Points

- Treat migration as a terminal state transition; block future bonding-curve swaps after success.
- Validate the destination AMM config, fee mode, token order, and tick or price bounds.
- Use the same terminal-price math in tests, quotes, and migration execution.
- Account migration, partner, and protocol fees before burning surplus inventory.
- Emit migration events with the destination pool, seed amounts, price, fees, and surplus handling.
- Test underfilled, exactly-filled, overfilled, high-fee, and decimal-mismatch terminal states.

## Source Evidence

- Meteora Dynamic Bonding Curve computes migration state and calls AMM-specific migration handlers in `/private/tmp/defillama-source/MeteoraAg_dynamic-bonding-curve/programs/dynamic-bonding-curve/src/migration_handler/mod.rs`.
- Its migration handlers seed compounding and concentrated liquidity pools in `migration_handler/compounding_liquidity.rs` and `migration_handler/concentrated_liquidity.rs`, validate DAMM v2 configuration in `instructions/partner/ix_create_config.rs`, and test migration fee behavior in `programs/dynamic-bonding-curve/src/tests/test_migration_fee.rs`.

## Real-World Examples

- Meteora Dynamic Bonding Curve graduates launch liquidity into DAMM-style AMM pools through a terminal migration handler.

## Related Patterns

- [Activation-Scoped Launch Fee Scheduler](./pattern-activation-scoped-launch-fee-scheduler.md)
- [Canonical AMM Pool Factory](./pattern-canonical-amm-pool-factory.md)
- [User-Directed Liquidity Migrator](./pattern-user-directed-liquidity-migrator.md)

## References

- See Source Evidence.
