# Bytecode-Split Extension Delegate

> Split oversized contract code into a primary contract and an extension delegate that serves selected functions through fallback `delegatecall`.

## Metadata

| Property | Value |
|----------|-------|
| Category | upgrades |
| Tags | upgrade, delegatecall, extension, bytecode-size, storage |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A contract approaches bytecode size limits
- Extension functions need access to the same storage layout
- The delegate target can be immutable or tightly governed
- Selector ownership and storage compatibility can be tested

## Avoid When

- The extension target can be swapped without review
- Selectors can collide silently with primary contract functions
- Storage layout is not shared and locked
- Users or integrators cannot tell which functions are extension-backed

## How It Works

The primary contract handles core functions and delegates unknown selectors:

```solidity
fallback() external payable {
    address target = extensionDelegate;
    (bool ok, bytes memory data) = target.delegatecall(msg.data);
    if (!ok) revertWith(data);
    returnWith(data);
}
```

The extension imports the same storage layout and implements secondary functions.

## Key Points

- Review selector collisions across primary and extension functions.
- Keep extension delegate immutable or behind strict versioned upgrade controls.
- Test extension calls through the primary contract, not only directly.
- Run storage layout checks on both code units.
- Document which APIs are extension-backed.

## Source Evidence

- Compound III Comet delegates unrecognized selectors to `CometExt`, which implements extension functions over shared storage and is tested through the main Comet contract.

## Related Patterns

- [Diamond Selector Collision Risk](./risk-diamond-selector-collision.md)
- [Namespaced Storage Accessor](./pattern-namespaced-storage-accessor.md)
- [Delegatecall Context Confusion](../../ANTIPATTERNS.md#delegatecall-context-confusion)
