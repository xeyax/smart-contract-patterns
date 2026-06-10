# Fee-Pool Capped Asymmetric Funding

> Cap protocol-paid funding by fee-pool reserves and allow side-specific funding when symmetric rates would overdraw the pool.

## Metadata

| Property | Value |
|----------|-------|
| Category | perps |
| Tags | perps, funding, fee-pool, insurance, imbalance |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Funding can be paid from protocol reserves or a fee pool
- Long and short open interest can become materially imbalanced
- Symmetric funding would require the protocol to pay more than available reserves
- The market can disclose side-specific funding rates to traders

## Avoid When

- Funding is always strictly trader-to-trader with no protocol reserve exposure
- Side-specific funding would violate market design or user expectations
- Fee-pool depletion cannot be measured before applying the funding update
- Funding-rate changes are hidden from quotes, liquidation math, or risk checks

## Trade-offs

**Pros:**
- Prevents funding updates from overdrawing protocol reserves
- Keeps the market updateable when one side cannot fully pay the other
- Makes reserve-backed funding exposure explicit

**Cons:**
- Side-specific rates are harder for users and integrators to model
- Fee-pool caps can reduce funding convergence during extreme imbalance
- Requires careful rounding and reserve-depletion tests

## How It Works

Compute uncapped funding first. If the side receiving funding would require a
protocol-paid amount above the available fee pool, cap the protocol-paid portion
and derive side-specific rates.

```rust
fn update_funding(market: &mut Market) {
    let funding = calculate_symmetric_funding(market);
    let protocol_payment = funding.protocol_paid_amount();

    if protocol_payment > market.fee_pool_available {
        let capped = market.fee_pool_available;
        market.long_funding_rate = derive_long_rate(funding, capped);
        market.short_funding_rate = derive_short_rate(funding, capped);
    } else {
        market.long_funding_rate = funding.rate;
        market.short_funding_rate = funding.rate;
    }
}
```

## Implementation

- Separate trader-to-trader funding from protocol-paid funding.
- Cap protocol-paid funding by current fee-pool or reserve availability.
- Define rounding direction for each side and for tiny updates.
- Surface side-specific funding in account health and liquidation math.
- Test balanced OI, imbalanced OI, empty fee pool, partial fee pool, and repeated small updates.

## Source Evidence

- Drift computes funding with capped reserve payments and side-specific funding-rate behavior in [`programs/drift/src/math/funding.rs`](https://github.com/drift-labs/protocol-v2/blob/0ae3e3b1db782a6765c3525b3dec38ad4d9d3a62/programs/drift/src/math/funding.rs) and applies updates in `programs/drift/src/controller/funding.rs`.
- Drift tests cover reserve-capped and imbalanced funding cases in `programs/drift/src/math/funding/tests.rs`.

## Real-World Examples

- Drift Protocol caps funding paid from fee-pool reserves and permits asymmetric side funding under imbalance.

## Related Patterns

- [ADL Reserve And Funding Risk Controls](./req-adl-reserve-and-funding-risk-controls.md)
- [Capped PnL Impact Pool Risk Accounting](./pattern-capped-pnl-impact-pool-risk-accounting.md)
- [Toxic Liquidation Spiral](../../ANTIPATTERNS.md#toxic-liquidation-spiral)

## References

- Drift Protocol funding math and controller source.
