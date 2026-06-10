# Version-Gated Message Endpoint Registry

> Register immutable messenger endpoint versions and let applications accept only registry-known endpoints at or above a monotonic minimum version.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, messaging, registry, versioning, endpoint |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A cross-chain messaging protocol deploys immutable endpoint contracts by version
- Applications need controlled migration from old endpoints to new endpoints
- Endpoint addresses can be registered before or after deployment through an authenticated path
- A compromised endpoint should be paused without replacing the whole application

## Avoid When

- The endpoint is an upgradeable proxy with a single stable address and storage continuity
- Applications cannot tolerate old in-flight messages being rejected after a minimum-version bump
- The registry update path lacks source-chain, sender, destination, and version-increment checks
- Version numbers can be reused, decreased, or skipped without explicit migration rules

## Trade-offs

**Pros:**
- Immutable per-version endpoints avoid the storage-collision and upgrade risks of a single proxy endpoint.
- Per-endpoint pause isolates a compromised version without redeploying or migrating applications.
- Monotonic minimum versions let applications force migration off vulnerable endpoints.
- Authenticated registry updates with version-increment checks block rogue endpoint registration.

**Cons:**
- Minimum-version bumps can strand in-flight messages sent through older endpoints — a real liveness hazard requiring migration coordination.
- Every receive pays registry lookups (version resolution plus pause check), adding gas and an external-call dependency per message.
- Pre-registered deterministic future addresses must be bytecode-verified separately before they can be trusted.
- Migration choreography — pin vs latest, grace windows, route-scoped library overlap — is complex to operate and easy to misconfigure.
- The registry becomes a critical shared dependency: if its authenticated update path breaks, endpoint evolution halts protocol-wide.

## How It Works

The registry stores a bidirectional mapping between endpoint versions and
addresses. New versions are added only through an authenticated governance or
cross-chain message path, and the latest version advances monotonically:

```solidity
function addEndpointVersion(VersionEntry calldata entry, Proof calldata proof) external {
    require(_verifiedRegistryMessage(entry, proof), "bad registry proof");
    require(entry.version != 0, "zero version");
    require(versionToAddress[entry.version] == address(0), "version exists");
    require(entry.version <= latestVersion + MAX_INCREMENT, "jump");

    versionToAddress[entry.version] = entry.endpoint;
    addressToVersion[entry.endpoint] = max(addressToVersion[entry.endpoint], entry.version);
    if (entry.version > latestVersion) latestVersion = entry.version;
}
```

Applications receive messages only from registered endpoints whose version is at
least the application's configured minimum:

```solidity
function receiveMessage(bytes calldata payload) external {
    uint256 version = registry.versionOf(msg.sender);
    require(version >= minEndpointVersion, "old endpoint");
    require(!pausedEndpoint[msg.sender], "endpoint paused");
    _receive(payload);
}

function updateMinEndpointVersion(uint256 version) external onlyGovernance {
    require(version > minEndpointVersion, "not monotonic");
    require(version <= registry.latestVersion(), "unknown version");
    minEndpointVersion = version;
}
```

Because minimum-version changes can strand messages sent through older
endpoints, they should be treated as critical liveness parameters.

## Key Points

- Register immutable endpoint versions instead of mutating endpoint code in place.
- Authenticate registry updates by source chain, origin sender, destination registry, version, and endpoint address.
- Enforce monotonic latest and minimum versions.
- Let applications send through the latest endpoint or a pinned endpoint intentionally.
- Add per-endpoint pause controls for emergency isolation.
- Treat minimum-version bumps as exit and message-liveness risks for in-flight messages.
- If deterministic future addresses are registered before deployment, verify bytecode separately before relying on the endpoint.
- Distinguish global endpoint-version gates from route-scoped library migration: a route can accept an old receive library during a grace window even when the endpoint address itself does not change.

## Source Evidence

- Avalanche ICM Teleporter's registry accepts verified Warp off-chain messages for new protocol versions, stores version/address mappings, advances `latestVersion`, and allows future protocol addresses to be registered before deployment in [`contracts/teleporter/registry/TeleporterRegistry.sol`](https://github.com/ava-labs/icm-contracts/blob/0b68b03c906d17850712b49aa20f2dc18ed55568/contracts/teleporter/registry/TeleporterRegistry.sol).
- `TeleporterRegistryApp` accepts messages only from registry-known Teleporter addresses at or above a monotonic minimum version and can pause individual endpoint addresses in [`contracts/teleporter/registry/TeleporterRegistryApp.sol`](https://github.com/ava-labs/icm-contracts/blob/0b68b03c906d17850712b49aa20f2dc18ed55568/contracts/teleporter/registry/TeleporterRegistryApp.sol).
- LayerZero V2's per-route message library migration in [`packages/layerzero-v2/evm/protocol/contracts/MessageLibManager.sol`](https://github.com/LayerZero-Labs/LayerZero-v2/blob/9c741e7f9790639537b1710a203bcdfd73b0b9ac/packages/layerzero-v2/evm/protocol/contracts/MessageLibManager.sol) is related but distinct: the endpoint address stays fixed while OApps migrate send and receive libraries.

## Related Patterns

- [Deterministic Cross-Chain Factory](./pattern-deterministic-cross-chain-factory.md)
- [Canonical Bridge Counterpart Validation](./pattern-canonical-bridge-counterpart-validation.md)
- [Route-Scoped Message Library Migration](./pattern-route-scoped-message-library-migration.md)
- [Timelocked Address Registry](../upgrades/pattern-timelocked-address-registry.md)
