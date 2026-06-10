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

## Trade-offs

**Pros:**
- Core contracts keep aggressive storage packing for gas while consumers get structured, named read models.
- No privileged write path, so a resolver bug or compromise cannot mutate core state.
- Decoding logic can be fixed or extended by redeploying the resolver without touching the audited core.
- Stable domain structs simplify UIs, keepers, and integrations that would otherwise hand-decode packed words.

**Cons:**
- Resolver decode logic can drift from the core storage layout after upgrades, silently serving wrong values.
- Every core layout change requires a matched resolver release and deprecation of old versions — ongoing operational burden.
- Reimplemented decoding duplicates core semantics, so output must be regression-tested against direct core operations.
- Consumers may keep using stale or unofficial resolvers as if authoritative after an upgrade.
- On-chain composability pays an extra external call per read versus native view functions on the core.

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
