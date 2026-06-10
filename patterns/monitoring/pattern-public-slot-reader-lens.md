# Public Slot Reader Lens

> Expose efficient public reads for packed or singleton storage through typed slot-reader functions and libraries.

## Metadata

| Property | Value |
|----------|-------|
| Category | monitoring |
| Tags | monitoring, storage, lens, singleton, reads |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- Core state is packed, nested, or keyed in a singleton contract
- Off-chain indexers and periphery contracts need stable low-cost reads
- Storage layout is immutable or versioned
- Typed libraries can decode slots into meaningful domain data

## Avoid When

- Storage layout can drift without versioning
- Slot reads expose sensitive internal data or create unsafe coupling
- A standard view interface can provide the same data clearly

## Trade-offs

**Pros:**
- One generic `extsload`-style reader serves all current and future state without adding a view function per field, keeping core bytecode small.
- Raw slot reads are cheaper than layered getters, and batched slot reads cut indexer and periphery query costs.
- Typed decode libraries centralize layout knowledge, so consumers get domain types instead of hand-rolled offset math.
- Transient-storage readers expose operation-scoped state (e.g., live deltas) that conventional views cannot reach mid-transaction.

**Cons:**
- The storage layout becomes a public API: any slot or packing change is a breaking change for every consumer, forcing versioned readers and migration coordination.
- Slot-calculation bugs in decode libraries return plausible garbage rather than reverting, so every slot derivation needs tests against the writing code.
- Raw readers expose stale lazily-accrued values; consumers who skip explicit accrual make value-bearing decisions on wrong numbers.
- Generic slot access bypasses any read-side gating, so sensitive internal state cannot be selectively hidden once the reader exists.
- Layout knowledge duplicated into periphery libraries and indexers creates tight coupling that makes core refactors expensive.

## How It Works

Expose raw slot reads and pair them with typed libraries:

```solidity
function extsload(bytes32 slot) external view returns (bytes32 value) {
    assembly {
        value := sload(slot)
    }
}

function getPoolState(address manager, PoolId id) internal view returns (PoolState memory state) {
    bytes32 slot = poolStateSlot(id);
    bytes32 packed = IExtsload(manager).extsload(slot);
    return decodePoolState(packed);
}
```

Transient storage readers can expose operation-scoped state to trusted periphery during the same transaction.

## Key Points

- Treat slot-reader APIs as layout commitments.
- Pair raw readers with typed decode libraries.
- Version readers when storage layout changes.
- Avoid using slot readers as a substitute for authorization or invariant checks.
- Test every slot calculation against storage-writing code.
- Warn consumers when raw slot readers expose stale accounting that still needs explicit accrual before value-bearing decisions.

## Source Evidence

- Uniswap V4 exposes `extsload` and `exttload` style readers and typed state libraries for singleton pool and transient delta storage.
- Morpho Blue exposes raw `extSloads` plus typed periphery storage libraries for market, position, and singleton state in [`src/libraries/periphery`](https://github.com/morpho-org/morpho-blue/blob/1478e9cfe1b4d514f80682b3b60e4e12ff3ee45a/src/libraries/periphery), with tests for slot calculations.

## Related Patterns

- [Read-Only Storage Resolver Facade](./pattern-read-only-storage-resolver-facade.md)
- [Namespaced Storage Accessor](../upgrades/pattern-namespaced-storage-accessor.md)
- [Storage Layout Drift](../../ANTIPATTERNS.md#storage-layout-drift)
