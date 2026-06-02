# Mutual Parameter Acceptance

> Require both affected parties to accept shared economic parameters before the new values take effect.

## Metadata

| Property | Value |
|----------|-------|
| Category | access-control |
| Tags | access-control, parameters, fees, bilateral, acceptance |
| Complexity | Low |
| Gas Efficiency | High |
| Audit Risk | Low |

## Use When

- A parameter affects two independent parties, such as manager and user, partner and protocol, or splitter recipients
- Either party should be able to reject unilateral fee or ownership changes
- Off-chain negotiation should be reflected by on-chain acceptance

## Avoid When

- A single governance body legitimately owns the parameter
- Emergency risk parameters need immediate unilateral change
- One party cannot reliably submit acceptance transactions

## How It Works

```solidity
struct PendingParams {
    uint256 feeBps;
    bool acceptedByA;
    bool acceptedByB;
}

function proposeParams(uint256 feeBps) external onlyParty {
    pending = PendingParams({feeBps: feeBps, acceptedByA: false, acceptedByB: false});
}

function acceptParams() external onlyParty {
    if (msg.sender == partyA) pending.acceptedByA = true;
    if (msg.sender == partyB) pending.acceptedByB = true;

    if (pending.acceptedByA && pending.acceptedByB) {
        activeFeeBps = pending.feeBps;
        delete pending;
    }
}
```

## Key Points

- Reset acceptances when proposed values change.
- Bound parameter values even if both parties accept.
- Emit both proposal and acceptance events.
- Add expiry or cancellation for stale proposals.
- Do not use this as a substitute for governance review on system-wide parameters.

## Source Evidence

- Convex joint vault management requires both parties to accept fee-related parameters before applying them, with tests rejecting unilateral changes.

## Related Patterns

- [Two-Step Authority Handoff](./pattern-two-step-authority-handoff.md)
- [Unrestricted Admin](../../ANTIPATTERNS.md#unrestricted-admin)
