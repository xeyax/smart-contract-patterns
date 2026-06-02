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

### Call-Forwarding Variant

Selector scoping is especially important when a manager forwards calls on behalf of users or nodes. The forwarder should bind all three dimensions:

```solidity
require(allowedUser[user], "user");
require(allowedTarget[target], "target");
require(allowedSelector[target][selector], "selector");
```

A denylist of known-bad selectors is weaker than an allowlist because new target functions or proxy upgrades can create fresh bypasses.

### Merkle Permission Manifest Variant

For large operational permission sets, store a Merkle root of allowed calls and require each forwarded call to prove membership in the manifest:

```solidity
function manage(address target, bytes calldata data, bytes32[] calldata proof) external {
    bytes4 selector = bytes4(data);
    bytes32 leaf = keccak256(abi.encode(target, selector, _sensitiveArgs(data)));
    require(MerkleProof.verify(proof, permissionRoot, leaf), "permission");
    target.call(data);
}
```

The leaf should include decoded sensitive arguments such as token, spender, protocol, amount cap, or recipient when the same selector can perform materially different actions.

A richer manifest can also bind value-transfer permission, callback expectations, hook configuration, and selected calldata words. That keeps a broad selector such as `call(bytes)` from becoming broad authority when only some arguments are safe.

## Key Points

- Scope permissions by both target and selector; selector-only roles are too broad across contracts.
- Treat functions that accept arbitrary targets, calldata, or implementation addresses as high-risk even if selector-scoped.
- Store and review a generated permission manifest in CI or deployment artifacts.
- For Merkle manifests, include sensitive decoded arguments in the leaf when selector-level approval is too broad.
- Prefer timelocks for selectors that change assets, upgrade code, alter fees, or pause exits.
- Keep emergency selectors separate from routine maintenance selectors.
- For call forwarders, scope by user, target, and selector; do not rely on selector blacklists.
- For bridge peer registration, delegated operators may initialize an unset route, but replacing an existing peer should be owner-only or timelocked because it redirects future message authentication.
- Operator routers that execute AVS or node-management calls should bind the operator, target, and selector; a privileged manager bypass remains a trusted path and should be documented separately.
- Swap or bridge executors should scope approval-only spenders separately from callable targets when `approveTo` differs from `callTo`.
- If a cross-chain governance router executes arbitrary target calldata after message authentication, the batch hash protects substitution but does not provide selector-scoped authority.
- Restaking module managers should bind module/operator identity, target, selector, and value-transfer permissions; a broad manager path that bypasses those fields is governance-grade authority.
- Managed vault execution should route calls through contract and asset guards that classify transaction type, public accessibility, and post-call tracking; replacing those guards is a privileged configuration change.

## Source Evidence

- Spiko checks target and selector masks before allowing protected calls and tests config-driven function requirements.
- Cap stores selector-scoped access rules and includes deployment checks that emit an observed access manifest.
- Ether.fi migrated call forwarding toward allowlisted user, target, and selector checks after identifying bypassable blacklist behavior.
- Veda uses a Merkle permission manifest for manager calls and includes target, selector, and decoded argument constraints for sensitive operations.
- Sophon's custom USDC bridge lets owner or admin initialize an unset chain bridge address, but reserves replacement of an existing chain bridge address to the owner in `/private/tmp/defillama-source/sophon-org__custom-usdc-bridge/src/L1USDCBridge.sol`.
- Aera v3 verifies guardian operations against Merkle leaves that bind target, selector, value flag, callback data, hook configuration, and extracted calldata in `/private/tmp/defillama-source/aera-finance__aera-contracts-public/v3/src/core/BaseVault.sol`.
- EtherFi AVS operator management routes calls by operator, target, and selector in `/private/tmp/defillama-source/etherfi-protocol_avs-smart-contracts/src/AvsOperatorManager.sol`, with operator execution in `src/AvsOperator.sol`.
- LI.FI allowlists target-selector pairs and uses a special approve-only selector for `approveTo` addresses that differ from swap call targets in `/private/tmp/defillama-source/lifinance__contracts/src/Libraries/LibAllowList.sol` and `src/Helpers/SwapperV2.sol`.
- Nomad governance router authenticates inbound governance batches but can execute arbitrary target calldata from accepted batches in `/private/tmp/defillama-source/nomad-xyz__monorepo/packages/contracts-core/contracts/governance/GovernanceRouter.sol`, making selector scoping a separate governance requirement.
- Puffer module management routes restaking operations through `/private/tmp/defillama-source/PufferFinance__puffer-contracts/mainnet-contracts/src/PufferModuleManager.sol` and `/private/tmp/defillama-source/PufferFinance__puffer-contracts/mainnet-contracts/src/PufferProtocol.sol`, with guardian payload checks in `/private/tmp/defillama-source/PufferFinance__puffer-contracts/mainnet-contracts/src/GuardianModule.sol`.
- dHEDGE manager execution resolves contract guards first, falls back to asset guards, validates transaction type and caller access, and optionally calls tracking guards after execution in `/private/tmp/defillama-source/dhedge__V2-Public/contracts/PoolLogic.sol`.

## Related Patterns

- [Two-Step Authority Handoff](./pattern-two-step-authority-handoff.md) - safe authority transfer
- [Unrestricted Admin](../../ANTIPATTERNS.md#unrestricted-admin) - broad-admin anti-pattern this mitigates
