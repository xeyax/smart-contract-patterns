# Open-Interest Scaled Margin Requirement

> Increase initial margin as market open interest approaches configured caps, reaching full collateralization at the upper bound.

## Metadata

| Property | Value |
|----------|-------|
| Category | perps |
| Tags | perps, open-interest, margin, exposure, risk |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A perpetual market wants soft exposure control rather than a hard open-interest stop
- Margin requirements can be computed from current or post-trade open interest
- Larger markets should become progressively more expensive to lever
- Match validation can simulate open-interest deltas before persisting them

## Avoid When

- The protocol requires strict hard caps with no additional fills near the cap
- Open interest cannot be measured consistently across long and short updates
- Margin changes would surprise users without quote-time disclosure

## Trade-offs

**Pros:**
- Makes leverage more expensive as market exposure grows
- Avoids a cliff at the open-interest limit
- Lets risk checks price a proposed trade before committing state

**Cons:**
- Requires careful post-trade margin simulation
- Can change execution feasibility as other trades update open interest
- Upper-cap behavior needs clear user and liquidation semantics

## How It Works

Initial margin is the base initial margin below a lower open-interest cap. Between
the lower and upper cap, the requirement scales upward. At the upper cap, margin
reaches 100% so new exposure is effectively fully collateralized.

```go
func initialMarginFraction(base, openInterest, lowerCap, upperCap Dec) Dec {
    if openInterest <= lowerCap {
        return base
    }
    if openInterest >= upperCap {
        return One
    }

    progress := (openInterest - lowerCap) / (upperCap - lowerCap)
    return base + progress * (One - base)
}
```

During match validation, apply the proposed open-interest delta to risk checks
before persisting the delta. Persist only after all balance and position updates
succeed.

## Implementation

- Define lower and upper open-interest caps per market or liquidity tier.
- Simulate post-trade open interest during collateral checks.
- Persist open-interest deltas only after successful state updates.
- Quote users against post-trade margin, not stale pre-trade margin.
- Test disabled caps, below lower cap, between caps, at upper cap, and state-revert paths.

## Source Evidence

- dYdX v4 describes lower and upper open-interest caps in [`proto/dydxprotocol/perpetuals/perpetual.proto`](https://github.com/dydxprotocol/v4-chain/blob/5ee9766351ef864856a309a971b13fdd98cae2c5/proto/dydxprotocol/perpetuals/perpetual.proto).
- dYdX computes adjusted initial margin in `protocol/x/perpetuals/types/liquidity_tier.go`.
- dYdX derives and applies open-interest deltas in `protocol/x/subaccounts/lib/oimf.go` and `protocol/x/subaccounts/keeper/subaccount.go`.
- dYdX tests OI-scaled margin behavior in `protocol/x/perpetuals/types/liquidity_tier_test.go` and subaccount keeper tests.

## Real-World Examples

- dYdX v4 scales initial margin requirements as market open interest grows.

## Related Patterns

- [Reserve Exposure Caps](../lending/pattern-reserve-exposure-caps.md)
- [Perps ADL, Reserve, And Funding Risk Controls](./req-adl-reserve-and-funding-risk-controls.md)
- [Capped PnL Impact Pool Risk Accounting](./pattern-capped-pnl-impact-pool-risk-accounting.md)

## References

- dYdX v4 liquidity tier and subaccount source.
