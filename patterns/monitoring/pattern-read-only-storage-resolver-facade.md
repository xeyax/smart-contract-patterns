# Read-Only Storage Resolver Facade

> Publish resolver contracts that decode packed core storage into stable read models without giving users direct write access to the core.

## Metadata

| Property | Value |
|----------|-------|
| Category | monitoring |
| Tags | monitoring, resolver, storage, packed-state, facade |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Core contracts pack storage aggressively for gas
- Users, UIs, and keepers need structured state views
- Official resolvers can be versioned with the core layout
- Read models should stay separate from state-changing logic

## Avoid When

- Storage layout is unstable and resolvers are not versioned
- The resolver reimplements business logic that can drift from the core
- Consumers can safely use simple view functions on the core contract

## How It Works

Resolvers read raw slots or compact getters and decode them into domain structs:

```solidity
function getUserPosition(address user, address token) external view returns (Position memory position) {
    bytes32 raw = core.readFromStorage(_positionSlot(user, token));
    position.supply = _decodeSupply(raw);
    position.borrow = _decodeBorrow(raw);
    position.lastUpdate = _decodeTimestamp(raw);
}
```

The resolver is read-only and has no privileged write path.

## Key Points

- Keep resolver versions tied to core storage-layout versions.
- Prefer domain structs and named fields over exposing raw packed words.
- Avoid adding hidden side effects or fallback writes to resolvers.
- Test resolver output against direct core operations.
- Document that unofficial resolvers can become stale after upgrades.

## Source Evidence

- Fluid uses periphery resolver contracts to decode packed liquidity and vault storage into stable read models, while core contracts keep gas-efficient packed accounting.

## Related Patterns

- [Public Slot Reader Lens](./pattern-public-slot-reader-lens.md)
- [Read-Only Protocol Health Checker](./pattern-read-only-protocol-health-checker.md)
- [Leaky Abstraction](../../ANTIPATTERNS.md#leaky-abstraction)
