# Version-Gated Upgrade Registry

> Authorize proxy upgrades only to implementation versions that a registry has approved and not deprecated.

## Metadata

| Property | Value |
|----------|-------|
| Category | upgrades |
| Tags | upgrade, proxy, registry, version, governance, beacon |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Many proxy instances should share a vetted implementation catalog
- Instance owners still need control over when to upgrade
- Old implementations may need deprecation without forcing immediate migration
- Integrators need a public list of supported versions

## Avoid When

- All instances must upgrade atomically through a single beacon
- The system has only one proxy and direct admin approval is simpler
- Governance cannot reliably review and register implementations

## Trade-offs

**Pros:**
- Separates implementation approval from per-instance upgrade timing
- Prevents accidental upgrade to unregistered code
- Supports deprecating known-bad versions
- Gives integrators a canonical version registry

**Cons:**
- Registry governance becomes critical infrastructure
- Deprecated versions may still be running until instance owners upgrade
- Version hashes and implementation metadata must be stable

## How It Works

```solidity
contract VersionRegistry {
    mapping(bytes32 => address) public implementationOf;
    mapping(bytes32 => bool) public deprecated;

    function registerVersion(bytes32 version, address implementation) external onlyGovernance {
        require(implementation.code.length != 0, "no code");
        implementationOf[version] = implementation;
    }

    function deprecateVersion(bytes32 version) external onlyGovernance {
        deprecated[version] = true;
    }
}

contract VersionedProxyAdmin {
    VersionRegistry public registry;

    function upgradeToVersion(ITransparentProxy proxy, bytes32 version) external onlyOwner {
        address implementation = registry.implementationOf(version);
        require(implementation != address(0), "unregistered");
        require(!registry.deprecated(version), "deprecated");

        proxy.upgradeTo(implementation);
    }
}
```

### Path-Specific Migrator Variant

Some systems need explicit upgrade paths instead of allowing every approved implementation to upgrade to every later version:

```solidity
mapping(bytes32 => mapping(bytes32 => address)) public migratorForPath;

function registerPath(bytes32 fromVersion, bytes32 toVersion, address migrator) external onlyGovernance {
    require(implementationOf[toVersion] != address(0), "unknown target");
    migratorForPath[fromVersion][toVersion] = migrator;
}

function upgrade(bytes32 toVersion, bytes calldata data) external onlyInstanceOwner {
    bytes32 fromVersion = currentVersion[msg.sender];
    address migrator = migratorForPath[fromVersion][toVersion];
    require(migrator != address(0), "path not approved");
    _delegateMigrate(migrator, data);
    currentVersion[msg.sender] = toVersion;
}
```

This separates implementation approval from per-path migration logic and prevents an instance from skipping required initializer or storage migration steps.

### Per-Instance Timelocked Opt-In Variant

When each proxy has its own owner, combine registry approval with a per-instance staged upgrade:

```solidity
function stageUpgrade(address proxy, address implementation) external onlyProxyOwner(proxy) {
    require(registry.canUseLogic(implementation), "unapproved");
    pending[proxy] = PendingUpgrade({
        implementation: implementation,
        applyAfter: block.timestamp + upgradeDelay
    });
}

function applyUpgrade(address proxy, address implementation) external {
    PendingUpgrade memory p = pending[proxy];
    require(p.implementation == implementation, "changed");
    require(block.timestamp >= p.applyAfter, "delay");
    _upgrade(proxy, implementation);
}
```

The exact implementation match prevents a different implementation from being substituted after the delay.

## Key Points

- Register code only after audit, bytecode verification, and storage layout checks.
- Deprecation should block new upgrades to a version without silently changing existing proxies.
- Instance owners must still be monitored; they can lag on critical upgrades.
- Emit version metadata that off-chain systems can map to source code and audit reports.
- For stateful upgrades, approve explicit `fromVersion -> toVersion` paths with path-specific migrators or initializers.
- If the registry can fail open after ownership is renounced or disabled, document that it no longer provides approved-implementation security.

## Source Evidence

- Reserve Index DTF gates proxy upgrades through a version registry and rejects unregistered or deprecated versions before upgrading.
- Tests cover registered upgrades and reject unregistered, deprecated, non-owner, and direct-admin paths.
- Maple uses version registries with explicit upgrade paths and path-specific migration/initializer logic, separating implementation approval from per-instance execution.
- Lagoon combines registry-approved logic with per-instance delayed proxy upgrades and exact pending-implementation checks; its fail-open registry mode should be treated as a deliberate de-scoping of upgrade gating.
- Reserve Protocol core upgrades `Main` and `RToken` only through registered, non-deprecated implementations and tests registered, deprecated, and unregistered upgrade paths in [`contracts/registry/VersionRegistry.sol`](https://github.com/reserve-protocol/protocol/blob/9cda9d89c871e70886fc4453f94fc6aa889445df/contracts/registry/VersionRegistry.sol) and `test/Upgradeability.test.ts`.

## Related Anti-Patterns

- [Beacon Proxy Single Point of Failure](../../ANTIPATTERNS.md#beacon-proxy-single-point-of-failure)
- [Storage Layout Drift](../../ANTIPATTERNS.md#storage-layout-drift)
