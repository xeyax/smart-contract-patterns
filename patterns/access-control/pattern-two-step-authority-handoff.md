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

## Source Evidence

- Rocket Pool stages guardian transfer and requires confirmation by the pending guardian.
- Rocket Pool node withdrawal addresses can be set through a pending confirmation path and reject confirmations from unrelated addresses.
- WBTC disables ownership renounce paths where continuing controller authority is required.

## Related Anti-Patterns

- [Unrestricted Admin](../../ANTIPATTERNS.md#unrestricted-admin)
- [Governance as Arbitrary Execution](../../ANTIPATTERNS.md#governance-as-arbitrary-execution)
