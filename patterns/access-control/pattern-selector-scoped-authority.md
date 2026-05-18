# Selector-Scoped Authority

> Grant operators permission to call specific function selectors on specific targets instead of granting broad owner or admin authority.

## Metadata

| Property | Value |
|----------|-------|
| Category | access-control |
| Tags | access-control, roles, selectors, permissions, operators |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Operators need to run recurring maintenance or risk-management calls
- Governance wants to delegate execution without delegating ownership
- A protocol has many functions with different risk levels
- Deployment or operations should produce an auditable permission manifest

## Avoid When

- The target function itself allows arbitrary calldata or target selection
- Selector permissions are generated manually without review
- The protocol cannot monitor which roles hold which selectors

## Trade-offs

**Pros:**
- Shrinks operator blast radius
- Makes permissions reviewable at target/selector granularity
- Lets governance revoke one operation without rotating all authority

**Cons:**
- More configuration state to audit
- Overloaded selectors and delegatecall paths need careful review
- Misconfigured manifests can give a false sense of least privilege

## How It Works

The permission manager maps `(target, selector, account)` to a role or permission bit:

```solidity
function canCall(address account, address target, bytes4 selector) public view returns (bool) {
    bytes32 permission = keccak256(abi.encode(target, selector));
    return hasPermission[permission][account];
}

modifier restricted() {
    require(permissionManager.canCall(msg.sender, address(this), msg.sig), "unauthorized");
    _;
}
```

Deployment scripts or maintenance checks should export the expected matrix:

```text
Vault.pauseProtocol        -> guardian
Vault.setFeeRecipient      -> timelock
Oracle.setBackupOracle     -> governance
```

## Key Points

- Scope permissions by both target and selector; selector-only roles are too broad across contracts.
- Treat functions that accept arbitrary targets, calldata, or implementation addresses as high-risk even if selector-scoped.
- Store and review a generated permission manifest in CI or deployment artifacts.
- Prefer timelocks for selectors that change assets, upgrade code, alter fees, or pause exits.
- Keep emergency selectors separate from routine maintenance selectors.

## Source Evidence

- Spiko checks target and selector masks before allowing protected calls and tests config-driven function requirements.
- Cap stores selector-scoped access rules and includes deployment checks that emit an observed access manifest.

## Related Patterns

- [Two-Step Authority Handoff](./pattern-two-step-authority-handoff.md) - safe authority transfer
- [Unrestricted Admin](../../ANTIPATTERNS.md#unrestricted-admin) - broad-admin anti-pattern this mitigates
