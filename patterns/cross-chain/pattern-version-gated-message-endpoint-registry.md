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

- Avalanche ICM Teleporter's registry accepts verified Warp off-chain messages for new protocol versions, stores version/address mappings, advances `latestVersion`, and allows future protocol addresses to be registered before deployment in `/private/tmp/defillama-source/ava-labs__icm-contracts/contracts/teleporter/registry/TeleporterRegistry.sol`.
- `TeleporterRegistryApp` accepts messages only from registry-known Teleporter addresses at or above a monotonic minimum version and can pause individual endpoint addresses in `/private/tmp/defillama-source/ava-labs__icm-contracts/contracts/teleporter/registry/TeleporterRegistryApp.sol`.
- LayerZero V2's per-route message library migration in `/private/tmp/defillama-source/LayerZero-Labs__LayerZero-v2/packages/layerzero-v2/evm/protocol/contracts/MessageLibManager.sol` is related but distinct: the endpoint address stays fixed while OApps migrate send and receive libraries.

## Related Patterns

- [Deterministic Cross-Chain Factory](./pattern-deterministic-cross-chain-factory.md)
- [Canonical Bridge Counterpart Validation](./pattern-canonical-bridge-counterpart-validation.md)
- [Route-Scoped Message Library Migration](./pattern-route-scoped-message-library-migration.md)
- [Timelocked Address Registry](../upgrades/pattern-timelocked-address-registry.md)
