# Route-Scoped Message Library Migration

> Migrate cross-chain message libraries per application route while accepting the old receive library for a bounded grace window.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, messaging, library, migration, route |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Applications can choose send or receive libraries per remote endpoint
- In-flight messages from the old receive library must remain deliverable
- The protocol can register and type-check supported message libraries
- Library changes are security-critical route configuration, not ordinary app settings

## Avoid When

- The endpoint is an upgradeable proxy with one continuous message verifier
- Old messages can be deterministically drained before a cutover
- Library registration or route changes can be made by an unbounded immediate admin
- Applications cannot monitor which library is accepted for each remote route

## Trade-offs

**Pros:**
- Lets one route migrate without forcing every application through the same cutover
- Preserves liveness for messages verified by the previous receive library
- Makes library trust explicit in route configuration

**Cons:**
- Grace windows temporarily expand the accepted verifier set
- Misconfigured old-library timeouts can strand or over-accept messages
- Route state is harder to audit than one global endpoint version

## How It Works

Each application route stores the active send and receive libraries. When a
receive library changes, the old library can be retained as a timeout entry
until a block or time deadline:

```solidity
function setReceiveLibrary(address app, uint32 srcDomain, address newLib, uint256 graceBlocks) external {
    _requireAppAdmin(app);
    _requireRegisteredReceiveLibrary(newLib, srcDomain);

    address oldLib = receiveLibrary[app][srcDomain];
    receiveLibrary[app][srcDomain] = newLib;

    if (graceBlocks == 0) {
        delete receiveLibraryTimeout[app][srcDomain];
    } else {
        require(oldLib != DEFAULT_LIB && newLib != DEFAULT_LIB, "explicit libs only");
        receiveLibraryTimeout[app][srcDomain] = Timeout(oldLib, block.number + graceBlocks);
    }
}

function verify(Route calldata route, bytes32 payloadHash) external {
    require(_isActiveOrGraceReceiveLib(route.app, route.srcDomain, msg.sender), "bad library");
    _recordVerifiedPayload(route, payloadHash);
}
```

## Implementation

```solidity
function _isActiveOrGraceReceiveLib(
    address app,
    uint32 srcDomain,
    address actualLib
) internal view returns (bool) {
    address expected = _resolveReceiveLibrary(app, srcDomain);
    if (actualLib == expected) return true;

    Timeout memory timeout = _resolveReceiveLibraryTimeout(app, srcDomain);
    return timeout.lib == actualLib && timeout.expiry > block.number;
}
```

### Key Points

- Register libraries before use and check whether they support the target domain.
- Separate send-library migration from receive-library migration; only receive libraries need old-message grace handling.
- Emit route, old library, new library, and expiry for monitoring.
- Treat grace-period extension as a security and liveness change.
- Test old-library acceptance during grace, old-library rejection after expiry, default-library transitions, and unsupported-domain rejection.

## Source Evidence

- LayerZero V2 stores per-OApp send and receive libraries plus receive-library timeouts in [`packages/layerzero-v2/evm/protocol/contracts/MessageLibManager.sol:25`](https://github.com/LayerZero-Labs/LayerZero-v2/blob/9c741e7f9790639537b1710a203bcdfd73b0b9ac/packages/layerzero-v2/evm/protocol/contracts/MessageLibManager.sol#L25).
- LayerZero V2 validates either the current receive library or the timeout library in `MessageLibManager.sol:105`.
- LayerZero V2 OApps can set per-route receive libraries with grace periods in `MessageLibManager.sol:245`.
- LayerZero V2 endpoint verification rejects messages from invalid receive libraries before recording payload hashes in [`packages/layerzero-v2/evm/protocol/contracts/EndpointV2.sol:151`](https://github.com/LayerZero-Labs/LayerZero-v2/blob/9c741e7f9790639537b1710a203bcdfd73b0b9ac/packages/layerzero-v2/evm/protocol/contracts/EndpointV2.sol#L151).
- LayerZero V2 tests cover default and non-default receive-library grace behavior in [`packages/layerzero-v2/evm/protocol/test/MessageLibManager.t.sol`](https://github.com/LayerZero-Labs/LayerZero-v2/blob/9c741e7f9790639537b1710a203bcdfd73b0b9ac/packages/layerzero-v2/evm/protocol/test/MessageLibManager.t.sol).

## Real-World Examples

- LayerZero V2 - OApp and default message libraries can be migrated per endpoint with old-library receive grace windows.

## Related Patterns

- [Version-Gated Message Endpoint Registry](./pattern-version-gated-message-endpoint-registry.md)
- [Canonical Bridge Counterpart Validation](./pattern-canonical-bridge-counterpart-validation.md)
- [Bridge Exit Liveness Requirements](./req-bridge-exit-liveness.md)
- [Unrestricted Admin](../../ANTIPATTERNS.md#unrestricted-admin)

## References

- See Source Evidence.
