# Namespaced Storage Accessor

> Isolate upgradeable contract state behind explicit namespace slots and typed accessor libraries.

## Metadata

| Property | Value |
|----------|-------|
| Category | upgrades |
| Tags | upgrade, storage, eip-7201, namespace, uups |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Contracts are upgradeable and use inheritance or libraries
- Multiple modules need independent storage layouts
- Storage layout drift would be catastrophic
- CI can run storage and upgrade smoke tests

## Avoid When

- Contracts are immutable
- A simple append-only storage layout is sufficient and well enforced
- Developers are unlikely to maintain namespace constants carefully

## Trade-offs

**Pros:**
- Eliminates inheritance-order storage collisions; each module's state lives in its own deterministic slot.
- Modules can be added, removed, or reordered across upgrades without shifting other modules' layouts.
- The EIP-7201-style slot formula is verifiable offline and diffable in CI.
- Typed accessor libraries keep all state access auditable through one chokepoint per namespace.

**Cons:**
- Every state access pays an extra slot computation and assembly indirection versus plain declared variables.
- Boilerplate per module: namespace constant, struct, accessor; discipline failure (reused or edited namespace string) silently corrupts state.
- Struct field reordering or insertion inside a namespace is still a layout break; the pattern moves the hazard, it does not remove it.
- Off-the-shelf storage-layout tooling and explorers understand declared variables better than assembly-sloted structs, weakening automated checks unless CI is extended.

## How It Works

Define a stable namespace and expose one accessor:

```solidity
library VaultStorageUtils {
    bytes32 internal constant STORAGE_SLOT =
        keccak256(abi.encode(uint256(keccak256("protocol.storage.Vault")) - 1)) & ~bytes32(uint256(0xff));

    struct VaultStorage {
        uint256 totalAssets;
        mapping(address => uint256) balances;
    }

    function getStorage() internal pure returns (VaultStorage storage $) {
        bytes32 slot = STORAGE_SLOT;
        assembly {
            $.slot := slot
        }
    }
}
```

Contract logic reads and writes through the accessor instead of declaring mutable variables directly.

## Key Points

- Namespace strings must be stable and unique.
- Do not reuse a namespace for unrelated modules.
- Keep struct field changes append-only unless a migration is explicit.
- Run upgrade smoke tests that verify existing state survives an implementation change.
- Combine with storage layout diffing in CI.

## Source Evidence

- Cap uses storage utility libraries with explicit namespace slots and upgrade smoke tests over live state.

## Related Patterns

- [Version-Gated Upgrade Registry](./pattern-version-gated-upgrade-registry.md)
- [Storage Layout Drift](../../ANTIPATTERNS.md#storage-layout-drift)
