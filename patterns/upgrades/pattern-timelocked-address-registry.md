# Timelocked Address Registry

> Resolve module addresses by registry IDs while staging each address change behind a per-entry wait period.

## Metadata

| Property | Value |
|----------|-------|
| Category | upgrades |
| Tags | upgrade, registry, timelock, modules, address-book |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Executors or routers resolve modules, actions, wrappers, or adapters by ID
- Module replacement should not require redeploying every caller
- Users and bots need time to observe address changes
- Different entries may have different risk and delay requirements

## Avoid When

- Module addresses should be immutable
- Registry admin is not protected by governance, multisig, or timelock
- Callers can bypass the registry with arbitrary targets
- Staged updates do not include enough metadata for monitoring

## How It Works

Each ID has a live address and an optional pending address with an activation time:

```solidity
function startChange(bytes32 id, address newAddress) external onlyAdmin {
    pending[id] = PendingChange({
        addr: newAddress,
        executeAfter: block.timestamp + waitPeriod[id]
    });
}

function approveChange(bytes32 id) external {
    require(block.timestamp >= pending[id].executeAfter, "wait");
    entries[id] = pending[id].addr;
    delete pending[id];
}
```

Callers use only live entries. Pending entries are visible for monitoring before activation.

## Key Points

- Use stable IDs and emit old, pending, and final addresses.
- Validate code length and expected interface where possible.
- Give high-risk entries longer delays.
- Allow cancellation of pending malicious or mistaken changes.
- Test callers against pending, removed, and unregistered entries.

## Source Evidence

- Defi Saver V3 resolves modules and action addresses through a registry with staged address changes and wait periods before approval.

## Related Patterns

- [Registry-Routed Wallet Recipes](../automation/pattern-registry-routed-wallet-recipes.md)
- [Version-Gated Upgrade Registry](./pattern-version-gated-upgrade-registry.md)
