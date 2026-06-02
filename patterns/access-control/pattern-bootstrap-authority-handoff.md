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

For one-shot upgrades, the temporary authority can be a narrowly scoped handoff
contract instead of a factory. The owner transfers authority to a contract whose
only job is to verify the intended implementation code hash, write exact storage
slots or registry entries, and return ownership to the final owner.

## Key Points

- Assert final owner, pauser, upgrader, and operator roles in tests.
- Emit deployment events that identify all created contracts and final authorities.
- If any handoff can fail, revert the whole deployment instead of leaving partial authority.
- Do not leave the factory as owner "for convenience."
- Combine with selector-scoped authority for any retained factory or operator permissions.
- For cross-chain factories, assert proxy admin, upgrade executor, beacon owner, implementation initialization, and gateway roles after both local and remote deployments.
- For temporary upgrade authorities, verify implementation bytecode or address inputs before writing storage, then return ownership in the same runbook.
- For cross-chain deployments, review the final authority matrix before activation: owner, delegate, proxy admin, Safe threshold, signer set, bytecode/compiler identity, queued Safe transactions, peer links, and route libraries.

## Source Evidence

- Wormhole NTT factory temporarily owns/configures manager and transceiver contracts, sets peers and limits, then transfers owner/pauser roles to the final owner contract.
- Tests assert final owner and pauser placement after factory deployment.
- Arbitrum token bridge deployment tests assert proxy admin, upgrade executor, beacon, owner, and initialized-logic placement after factory-driven bridge deployment.
- Mantle's legacy deployment includes `ChugSplashDictator` and `AddressDictator` contracts that temporarily receive authority, check an implementation code hash or set exact address-manager entries, then return ownership to the final owner.
- USDT0 deployment audit reports repeatedly verify final owner/delegate/proxy-admin placement, Safe threshold and signer composition, bytecode identity, and queued transaction state; this is audit-source evidence for the runbook checklist rather than implementation proof.

## Related Patterns

- [Selector-Scoped Authority](./pattern-selector-scoped-authority.md)
- [Two-Step Authority Handoff](./pattern-two-step-authority-handoff.md)
- [Unrestricted Admin](../../ANTIPATTERNS.md#unrestricted-admin)
