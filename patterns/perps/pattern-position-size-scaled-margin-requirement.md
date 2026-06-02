# Position-Size Scaled Margin Requirement

> Increase margin requirements and discount positive unrealized PnL as an individual position grows.

## Metadata

| Property | Value |
|----------|-------|
| Category | perps |
| Tags | perps, margin, position-size, pnl, risk |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Individual large positions are riskier than the same exposure split across smaller traders
- Margin should scale with position size, not only market-wide open interest
- Positive unrealized PnL should not be fully credited for very large exposure
- The margin engine can compute post-trade position size before accepting an order

## Avoid When

- Market risk is controlled only through hard per-account caps
- Position size is not reliably available during pre-trade checks
- PnL discounting would create unclear liquidation or withdrawal semantics
- Users cannot see the scaled margin impact before execution

## Trade-offs

**Pros:**
- Makes concentration risk more expensive at the account level
- Reduces reliance on market-wide OI caps alone
- Limits borrowable value from large unrealized profits

**Cons:**
- Adds nonlinear margin behavior users must quote correctly
- Can make partial fills or close paths sensitive to ordering
- Requires tests around PnL discount and liquidation thresholds

## How It Works

Compute a base margin requirement, then scale it upward as the position's absolute
size exceeds configured thresholds. Apply a similar or related discount to
positive unrealized PnL so large profitable positions cannot borrow or withdraw
against the full mark-to-market amount.

```rust
fn margin_requirement(position_size: u128, base_margin: Decimal) -> Decimal {
    let scale = size_scale(position_size);
    base_margin.max(base_margin * scale)
}

fn credited_unrealized_pnl(position_size: u128, pnl: i128) -> i128 {
    if pnl <= 0 {
        return pnl;
    }
    pnl * pnl_credit_weight(position_size) / PRECISION
}
```

## Implementation

- Define the position-size scaling function and maximum margin fraction.
- Apply scaling to post-trade size during order validation.
- Discount positive unrealized PnL before collateral withdrawal or new-risk checks.
- Keep close/reduce paths possible when they reduce risk.
- Test below threshold, between thresholds, max scale, positive PnL discount, and reduce-only behavior.

## Source Evidence

- Drift stores IMF factor and unrealized PnL scaling fields in `/private/tmp/defillama-source/drift-labs__protocol-v2/programs/drift/src/state/perp_market.rs`.
- Drift applies position-size-scaled margin and positive PnL discounts in `programs/drift/src/math/margin.rs`.
- Drift tests size-scaled margin behavior in `programs/drift/src/math/margin/tests.rs`.

## Real-World Examples

- Drift Protocol increases margin for large individual perp positions and discounts positive unrealized PnL as exposure grows.

## Related Patterns

- [Open-Interest Scaled Margin Requirement](./pattern-open-interest-scaled-margin-requirement.md)
- [Reserve Exposure Caps](../lending/pattern-reserve-exposure-caps.md)
- [Capped PnL Impact Pool Risk Accounting](./pattern-capped-pnl-impact-pool-risk-accounting.md)

## References

- Drift Protocol margin math source.
