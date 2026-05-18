# Selector-Routed Module Proxy

> Dispatch proxy fallback calls through a selector-to-implementation registry with reverse selector manifests and collision checks.

## Metadata

| Property | Value |
|----------|-------|
| Category | upgrades |
| Tags | proxy, selector, modules, upgrade, dispatch |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A system needs many modules behind one stable address
- Function selectors can be assigned to focused implementations
- Upgrades should add, replace, or remove selector groups independently
- Governance can review selector manifests before activation

## Avoid When

- A simple transparent or UUPS proxy is enough
- Selector ownership and storage layout cannot be audited per module
- The proxy allows duplicate selectors or silent selector replacement

## How It Works

The proxy maps each function selector to an implementation and delegates fallback calls:

```solidity
function setImplementation(address implementation, bytes4[] calldata selectors) external onlyGovernance {
    for (uint256 i; i < selectors.length; ++i) {
        require(selectorToImpl[selectors[i]] == address(0), "selector exists");
        selectorToImpl[selectors[i]] = implementation;
    }
    implementationSelectors[implementation] = selectors;
}

fallback() external payable {
    address implementation = selectorToImpl[msg.sig];
    require(implementation != address(0), "unknown selector");
    _delegate(implementation);
}
```

Reverse manifests let governance remove or inspect every selector owned by an implementation.

## Key Points

- Reject duplicate selectors unless replacement is an explicit staged operation.
- Keep reverse selector manifests for removals and audits.
- Use namespaced storage or strict shared-layout rules across modules.
- Emit selector-level add, replace, and remove events.
- Run selector-collision checks in CI and deployment scripts.

## Source Evidence

- Fluid's infinite proxy routes fallback calls by selector, maintains implementation selector sets, and rejects duplicate selector registration.

## Related Patterns

- [Bytecode-Split Extension Delegate](./pattern-bytecode-split-extension-delegate.md)
- [Namespaced Storage Accessor](./pattern-namespaced-storage-accessor.md)
- [Diamond Selector Collision](./risk-diamond-selector-collision.md)
