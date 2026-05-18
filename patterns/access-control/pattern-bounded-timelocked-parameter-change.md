# Bounded Timelocked Parameter Change

> Require critical parameter changes to be committed, delayed, bounded, and explicitly applied before they affect protocol economics.

## Metadata

| Property | Value |
|----------|-------|
| Category | access-control |
| Tags | access-control, timelock, parameters, bounds, governance |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Parameters affect fees, amplification, rates, caps, or admin recipients
- Users need time to react before a change activates
- A parameter can be bounded by protocol invariants
- Changes should be cancellable or superseded before activation

## Avoid When

- The parameter is harmless or purely cosmetic
- Emergency risk reduction must happen immediately
- Bounds are only social conventions and not enforced on-chain

## How It Works

Stage the change first:

```solidity
function commitFee(uint256 newFee) external onlyGovernance {
    require(newFee <= MAX_FEE, "fee too high");
    pendingFee = newFee;
    applyAfter = block.timestamp + delay;
}

function applyFee() external {
    require(block.timestamp >= applyAfter, "delay");
    fee = pendingFee;
}
```

For continuous changes such as AMM amplification ramps, also bound the maximum rate of change and minimum ramp duration.

## Key Points

- Enforce hard bounds in the commit function.
- Emit both commit and apply events.
- Treat delay reductions as critical changes.
- Make cancellation rules explicit.
- Test edge values, early apply attempts, and maximum-change constraints.

## Source Evidence

- Curve pool templates commit and apply fee/admin changes behind a delay and bound amplification ramps by duration and maximum factor changes.

## Related Patterns

- [Two-Step Authority Handoff](./pattern-two-step-authority-handoff.md)
- [Break-Glass Risk Limiter](./pattern-break-glass-risk-limiter.md)
- [Unrestricted Admin](../../ANTIPATTERNS.md#unrestricted-admin)
