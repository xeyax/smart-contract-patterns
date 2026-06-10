# Initial And Maintenance Leverage Gates

> Enforce stricter leverage bounds when opening or increasing a position, then use maintenance leverage bounds to block unsafe collateral removal and trigger liquidation.

## Metadata

| Property | Value |
|----------|-------|
| Category | perps |
| Tags | perps, leverage, margin, liquidation, risk |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Perpetual positions borrow pool liquidity against user collateral
- Opening or increasing exposure should require a stricter initial margin than ongoing maintenance
- Collateral removal can make an otherwise valid position liquidatable
- Liquidation eligibility should be computed from the same leverage model used by risk checks

## Avoid When

- The market uses portfolio margin or scenario shocks across many positions
- Margin requirements scale primarily by position size or open interest
- Liquidation is progressive and partial rather than a threshold state
- Oracle validity differs across open, close, collateral, and liquidation paths but is not modeled

## Trade-offs

**Pros:**
- Separates entry risk from maintenance risk in a simple, auditable model
- Prevents users from opening at the edge of liquidation
- Gives liquidators a deterministic threshold to monitor

**Cons:**
- Static leverage bands may underprice crowded or volatile markets
- Risk managers must tune per-custody or per-market min/max values carefully
- Does not define loss allocation after liquidation or reserve exhaustion

## How It Works

Configure minimum and maximum initial leverage for new or increased positions, plus maximum maintenance leverage for ongoing positions. Opening a position checks the initial bounds. Removing collateral checks that the remaining position still satisfies maintenance or initial policy, depending on the action. Liquidation checks the maintenance threshold and rejects attempts to liquidate healthy positions.

```rust
fn validate_open_position(position: &Position, custody: &Custody) -> Result<()> {
    let leverage = position.initial_leverage();
    require!(leverage >= custody.min_initial_leverage, LeverageTooLow);
    require!(leverage <= custody.max_initial_leverage, LeverageTooHigh);
    Ok(())
}

fn validate_liquidation(position: &Position, custody: &Custody) -> Result<()> {
    let leverage = position.current_leverage();
    require!(leverage > custody.max_maintenance_leverage, PositionHealthy);
    Ok(())
}
```

## Key Points

- Store initial and maintenance leverage limits per market, custody, or asset risk bucket.
- Validate configuration ordering so minimum, maximum, and maintenance values cannot contradict each other.
- Recheck leverage after collateral removal, size increase, funding accrual, or PnL updates.
- Use oracle prices with action-appropriate freshness for open, collateral, and liquidation paths.
- Keep liquidation payoff caps, reserve limits, and loss waterfalls separate from leverage eligibility.
- Test min/max initial leverage, healthy liquidation rejection, collateral-removal failure, and threshold crossing.

## Source Evidence

- Solana Labs Perpetuals stores initial and maintenance leverage limits in custody configuration in [`programs/perpetuals/src/state/custody.rs`](https://github.com/solana-labs/perpetuals/blob/ebfb4972ea5d1cde8580a7e8c7b9dbd1fdb2b002/programs/perpetuals/src/state/custody.rs).
- Solana Labs Perpetuals validates leverage through pool risk checks in [`programs/perpetuals/src/state/pool.rs`](https://github.com/solana-labs/perpetuals/blob/ebfb4972ea5d1cde8580a7e8c7b9dbd1fdb2b002/programs/perpetuals/src/state/pool.rs).
- Solana Labs Perpetuals applies leverage gates on open, collateral removal, and liquidation in [`programs/perpetuals/src/instructions/open_position.rs`](https://github.com/solana-labs/perpetuals/blob/ebfb4972ea5d1cde8580a7e8c7b9dbd1fdb2b002/programs/perpetuals/src/instructions/open_position.rs), `instructions/remove_collateral.rs`, and `instructions/liquidate.rs`.
- Solana Labs Perpetuals tests min/max leverage and liquidation thresholds in [`programs/perpetuals/tests/native/tests_suite/position/min_max_leverage.rs`](https://github.com/solana-labs/perpetuals/blob/ebfb4972ea5d1cde8580a7e8c7b9dbd1fdb2b002/programs/perpetuals/tests/native/tests_suite/position/min_max_leverage.rs) and `liquidate_position.rs`.

## Related Patterns

- [Position-Size Scaled Margin Requirement](./pattern-position-size-scaled-margin-requirement.md)
- [Open-Interest Scaled Margin Requirement](./pattern-open-interest-scaled-margin-requirement.md)
- [Progressive Liquidation State Machine](./pattern-progressive-liquidation-state-machine.md)
- [ADL Reserve And Funding Risk Controls](./req-adl-reserve-and-funding-risk-controls.md)
- [Capped PnL Impact Pool Risk Accounting](./pattern-capped-pnl-impact-pool-risk-accounting.md)
