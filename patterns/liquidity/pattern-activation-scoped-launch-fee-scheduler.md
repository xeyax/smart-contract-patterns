# Activation-Scoped Launch Fee Scheduler

> Taper AMM fees after pool activation using time, price-progress, or rate-limited launch schedules.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, launch, dynamic-fee, scheduler, activation |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- A new pool needs higher initial fees during launch or price discovery
- Fee schedule should start only after a configured activation point
- Fees should taper by elapsed time, market-cap progress, or bounded trade flow
- Launchpad or pool creators need predictable fee decay rules

## Avoid When

- Pool fees should remain fixed throughout the pool lifecycle
- Activation timing can be manipulated or is not enforced on-chain
- The schedule creates asymmetric trade restrictions that users cannot quote

## Trade-offs

**Pros:**
- Lets early launch volatility carry higher fees
- Makes fee decay deterministic and testable
- Can limit one-direction launch pressure without permanently penalizing swaps

**Cons:**
- More complex than a static fee
- Activation point, reference amount, and decay curve are sensitive parameters
- Directional rate limiters can surprise routers if not quoted correctly

## How It Works

The pool stores an activation point and one of several base-fee scheduler modes.
Before activation, launch actions may be disabled or use configured launch
behavior. After activation, the scheduler computes the current base fee.

```rust
fn base_fee(now: u64, price: u128, trade: TradeContext) -> u64 {
    match scheduler {
        Scheduler::TimeLinear { start_fee, end_fee, duration } => {
            interpolate(start_fee, end_fee, elapsed_since_activation(now), duration)
        }
        Scheduler::MarketCap { initial_price, target_price, start_fee, end_fee } => {
            interpolate_by_price_progress(start_fee, end_fee, price, initial_price, target_price)
        }
        Scheduler::RateLimiter { reference_amount, max_fee } => {
            bounded_directional_fee(trade, reference_amount, max_fee)
        }
    }
}
```

## Implementation

- Bind the schedule to an on-chain activation timestamp or slot.
- Cap minimum and maximum fees for every scheduler mode.
- Define whether schedules apply to both directions or only launch-sensitive directions.
- Quote fees through the same code path used by execution.
- If the fee is nonlinear per instruction or per buy window, reject same-pool swap fragmentation inside the same transaction or CPI sibling frame so traders cannot split one trade to evade the launch fee.
- Test pre-activation, exact activation, post-activation taper, cap behavior, and direction-specific trades.

## Source Evidence

- Meteora DAMM v2 defines time, rate-limiter, and market-cap scheduler modes in [`programs/cp-amm/src/state/fee.rs`](https://github.com/MeteoraAg/damm-v2/blob/58a13fcf45516a9f27f2bd2a2056fb66673454e0/programs/cp-amm/src/state/fee.rs).
- Meteora computes linear and exponential time tapering in `base_fee/fee_time_scheduler.rs`.
- Meteora reduces fees by market-cap or price progress in `base_fee/fee_market_cap_scheduler.rs`.
- Meteora scopes rate-limited launch fees in `base_fee/fee_rate_limiter.rs` and tests them in `programs/cp-amm/src/tests/test_rate_limiter.rs`.
- Meteora Dynamic Bonding Curve rejects repeated same-pool swap instructions in one transaction while rate-limited launch fees are active in [`programs/dynamic-bonding-curve/src/instructions/swap/ix_swap.rs`](https://github.com/MeteoraAg/dynamic-bonding-curve/blob/b4f954733f0e88258f1eb3f0eff75e4314c9610c/programs/dynamic-bonding-curve/src/instructions/swap/ix_swap.rs), with rate-limiter tests in `programs/dynamic-bonding-curve/src/tests/test_rate_limiter.rs`.

## Real-World Examples

- Meteora DAMM v2 uses activation-scoped fee scheduling for launch pools.

## Related Patterns

- [TWAP-Deviation Dynamic Fee](./pattern-twap-deviation-dynamic-fee.md)
- [Volatility Accumulator Dynamic Fee](./pattern-volatility-accumulator-dynamic-fee.md)
- [Offpeg Dynamic Fee](./pattern-offpeg-dynamic-fee.md)
- [Bonding-Curve Terminal Liquidity Cutover](./pattern-bonding-curve-terminal-liquidity-cutover.md)

## References

- Meteora DAMM v2 fee scheduler source.
