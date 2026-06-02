# User-Owned Proxy Vault

> Deploy one vault/proxy per user so protocol integrations can be automated while custody and position ownership remain isolated.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, proxy, clone, custody, external-protocol |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Users need individualized positions in an external protocol
- Shared vault custody would create unacceptable blast radius
- A manager should automate staking, reward claiming, or fee splits
- Cheap clone deployment is available

## Avoid When

- User positions are fully fungible and pooled accounting is simpler
- External protocol privileges require a shared operator account
- Users cannot understand per-vault ownership and migration obligations

## Trade-offs

**Pros:**
- Isolates user funds from other users' positions
- Limits damage from one proxy-specific bug or misconfiguration
- Lets protocol automation coexist with user-owned custody

**Cons:**
- More deployed contracts and operational overhead
- Each proxy may need lifecycle/deactivation handling
- Integrators must index many vault addresses

## How It Works

```solidity
function createVault(address user) external returns (address vault) {
    vault = implementation.clone();
    IUserVault(vault).initialize(user, protocolAdapter, rewardManager);
    registry[user] = vault;
}
```

The protocol can grant adapter privileges to the vault while the user remains owner of withdrawals or position control.

## Key Points

- Distinguish protocol operator privileges from user withdrawal ownership.
- Deactivate future vault creation separately from existing vault operation.
- Let old user vaults keep operating or migrate explicitly when implementations change.
- Avoid shared token custody unless internal ledgers and writer sets are explicit.

## Source Evidence

- Convex Frax-CVX platform deploys user-owned staking proxy vaults for external protocol positions while registry/booster contracts manage approved pool creation and reward flows.

## Related Patterns

- [Clone Factory](./pattern-clone-factory.md)
- [Shared Pool Sink](../../ANTIPATTERNS.md#shared-pool-sink)
