# Bootstrap Authority Handoff

> Let a factory hold temporary setup authority only long enough to wire a contract graph, then transfer all lasting roles to the intended owner.

## Metadata

| Property | Value |
|----------|-------|
| Category | access-control |
| Tags | access-control, factory, deployment, ownership, bootstrap |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- A factory deploys multiple contracts that must be configured atomically
- Peer links, limits, roles, or transceivers must be set before the system is usable
- The factory should not retain post-deployment control
- Tests can assert final role placement

## Avoid When

- Setup can be done directly by the final owner
- Any setup step depends on untrusted external callbacks
- The factory can be upgraded or reused to regain authority after handoff

## How It Works

```solidity
function deploySystem(Config calldata config, address finalOwner) external returns (System memory s) {
    s.manager = new Manager(address(this));
    s.transceiver = new Transceiver(address(this));

    s.manager.setPeers(config.peers);
    s.manager.setLimits(config.limits);
    s.transceiver.setManager(address(s.manager));

    s.manager.transferOwnership(finalOwner);
    s.manager.setPauser(finalOwner);
    s.transceiver.transferOwnership(finalOwner);
}
```

After deployment, no privileged role should remain with the factory except explicitly documented maintenance powers.

## Key Points

- Assert final owner, pauser, upgrader, and operator roles in tests.
- Emit deployment events that identify all created contracts and final authorities.
- If any handoff can fail, revert the whole deployment instead of leaving partial authority.
- Do not leave the factory as owner "for convenience."
- Combine with selector-scoped authority for any retained factory or operator permissions.

## Source Evidence

- Wormhole NTT factory temporarily owns/configures manager and transceiver contracts, sets peers and limits, then transfers owner/pauser roles to the final owner contract.
- Tests assert final owner and pauser placement after factory deployment.

## Related Patterns

- [Selector-Scoped Authority](./pattern-selector-scoped-authority.md)
- [Two-Step Authority Handoff](./pattern-two-step-authority-handoff.md)
- [Unrestricted Admin](../../ANTIPATTERNS.md#unrestricted-admin)
