# Two-Step Authority Handoff

> Stage critical authority or withdrawal-address changes and require confirmation by the new address before activation.

## Metadata

| Property | Value |
|----------|-------|
| Category | access-control |
| Tags | access-control, admin, ownership, withdrawal-address, confirmation |
| Complexity | Low |
| Gas Efficiency | High |
| Audit Risk | Low |

## Use When

- A privileged role controls upgrades, pausing, treasury movement, or withdrawal addresses
- Mistyped or compromised replacement addresses would be hard to recover from
- The new address can actively confirm ownership

## Avoid When

- Authority must rotate atomically during an emergency
- The new authority is a contract that cannot call confirmation functions
- The system already uses a governance timelock with explicit queued operations

## Trade-offs

**Pros:**
- Eliminates authority loss to mistyped or dead addresses because the new holder must prove it can transact
- Minimal surface: two storage slots, two small functions, cheap to deploy and audit
- The current authority can cancel a staged handoff before acceptance
- Composes cleanly with timelocks for higher-impact role changes

**Cons:**
- Requires the new authority to actively call accept, so passive contracts or cold-storage setups need extra tooling
- Rotation takes two transactions, which is slower than atomic transfer during an emergency
- A shared pending slot can be griefed when multiple incumbents can restage a different address
- Provides no protection against a compromised current authority staging an attacker who promptly accepts
- Renounce semantics must be handled separately or systems that need continuing authority for mint, pause, or upgrade can be bricked

## How It Works

```solidity
address public authority;
address public pendingAuthority;

function setPendingAuthority(address next) external onlyAuthority {
    require(next != address(0), "zero authority");
    pendingAuthority = next;
}

function acceptAuthority() external {
    require(msg.sender == pendingAuthority, "not pending");
    authority = pendingAuthority;
    pendingAuthority = address(0);
}
```

For withdrawal addresses, keep the old address active until the new address confirms, or require the current address to authorize immediate changes.

## Key Points

- Emit events for both staging and acceptance.
- Let the current authority cancel a pending handoff.
- Use a timelock for high-impact role changes if the current authority remains able to stage malicious changes.
- For withdrawal addresses, distinguish "current address approved" from "new address confirmed".
- Disable or constrain `renounceOwnership()` when the system requires continuing authority for minting, burning, pausing, or upgrades.
- For risk-bearing account ownership transfers, consider a three-party flow: current owner initiates, protocol admin or risk manager approves, and the pending owner accepts after checks prove no active orders, unsafe CPI context, or incompatible companion instructions.
- If multiple current authorities can overwrite the same pending role, define priority or require atomic stage-and-accept for forced replacements; otherwise an incumbent can grief the handoff by restaging another pending address.

## Source Evidence

- Rocket Pool stages guardian transfer and requires confirmation by the pending guardian.
- Rocket Pool node withdrawal addresses can be set through a pending confirmation path and reject confirmations from unrelated addresses.
- WBTC disables ownership renounce paths where continuing controller authority is required.
- Kamino Lend stages obligation ownership transfers through initiate, approve, accept, and abort states with transaction-context restrictions.
- Sophon's custom USDC bridge comments that owner-forced admin replacement must stage and accept atomically because the current admin can overwrite `pendingAdmin` in [`src/L1USDCBridge.sol`](https://github.com/sophon-org/custom-usdc-bridge/blob/72b36f11fb6c901380836043a43c738c434d5c12/src/L1USDCBridge.sol).

## Related Anti-Patterns

- [Unrestricted Admin](../../ANTIPATTERNS.md#unrestricted-admin)
- [Governance as Arbitrary Execution](../../ANTIPATTERNS.md#governance-as-arbitrary-execution)
