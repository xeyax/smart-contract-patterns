# Progressive Liquidation State Machine

> Liquidate unhealthy perpetual accounts through staged modes that bound size, elapsed time, price, dust cleanup, and bankruptcy fallback.

## Metadata

| Property | Value |
|----------|-------|
| Category | perps |
| Tags | perps, liquidation, state-machine, bankruptcy, dust |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Perpetual liquidations should scale with margin shortage rather than liquidating everything immediately
- The protocol needs different liquidation modes as time passes or risk worsens
- Liquidation price, size, and dust cleanup need explicit bounds
- Bankruptcy fallback is part of the solvency model

## Avoid When

- Liquidation is intentionally all-or-nothing
- The protocol cannot persist account liquidation mode or elapsed-time state
- Liquidators cannot reproduce the staged limits off-chain
- Bankruptcy or socialized-loss behavior is undefined

## Trade-offs

**Pros:**
- Reduces unnecessary position seizure for marginally unsafe accounts
- Makes liquidation escalation deterministic under stress
- Gives dust and bankruptcy paths explicit state-machine edges

**Cons:**
- More complex than a single health-factor threshold
- Incorrect mode transitions can trap accounts or delay needed liquidation
- Requires broad testing across time, price, and margin states

## How It Works

Record or derive a liquidation mode for the account. Each mode determines the
maximum liquidation size, elapsed-slot or elapsed-time escalation, limit price,
and whether dust or bankruptcy cleanup is permitted.

```rust
fn liquidate(account: &mut Account, market: &Market, now: Slot) {
    let mode = liquidation_mode(account, now);
    let max_size = max_liquidation_size(account.margin_shortage(), mode);
    let limit_price = liquidation_limit_price(account, market, mode);

    let filled = execute_liquidation(account, max_size, limit_price);
    if filled < account.min_remaining_position() && mode.allows_dust_cleanup() {
        close_dust(account);
    }
    if account.is_bankrupt() {
        resolve_bankruptcy(account, market);
    }
}
```

## Implementation

- Define liquidation modes and allowed transitions in a table.
- Bound liquidation size by margin shortage and mode.
- Include elapsed-time or elapsed-slot escalation rules.
- Require liquidation limit prices and oracle validity checks.
- Define dust cleanup and bankruptcy fallback separately from ordinary liquidation.
- Test mode transitions, partial liquidation, dust, stale oracle rejection, and bankruptcy fallback.

## Source Evidence

- Drift defines liquidation modes and mode transitions in `/private/tmp/defillama-source/drift-labs__protocol-v2/programs/drift/src/state/liquidation_mode.rs`.
- Drift bounds liquidation percentage, margin shortage, price, dust cleanup, and bankruptcy handling in `programs/drift/src/math/liquidation.rs` and `programs/drift/src/controller/liquidation.rs`.
- Drift tests progressive liquidation behavior in `programs/drift/src/math/liquidation/tests.rs`.

## Real-World Examples

- Drift Protocol liquidates perp accounts through staged liquidation modes with bounded size, elapsed-slot escalation, dust cleanup, and bankruptcy fallback.

## Related Patterns

- [Bounded Orderbook Liquidation Deleveraging](./pattern-bounded-orderbook-liquidation-deleveraging.md)
- [Capped PnL Impact Pool Risk Accounting](./pattern-capped-pnl-impact-pool-risk-accounting.md)
- [Toxic Liquidation Spiral](../../ANTIPATTERNS.md#toxic-liquidation-spiral)

## References

- Drift Protocol liquidation state and controller source.
