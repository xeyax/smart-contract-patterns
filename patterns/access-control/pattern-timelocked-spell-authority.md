# Timelocked Spell Authority

> Grant authority to scheduled action contracts only after a delay, with cancelability and separate emergency pause controls.

## Metadata

| Property | Value |
|----------|-------|
| Category | access-control |
| Tags | access-control, timelock, spell, governance, immutable |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A system is immutable or proxyless but still needs controlled authority changes
- Governance changes are bundled into reviewed action contracts
- The authority graph can grant and revoke permissions by contract address
- Emergency pause should remain separate from governance execution

## Avoid When

- The spell can execute arbitrary unreviewed calldata immediately
- There is no delay, cancellation path, or manifest for the scheduled spell
- Ordinary bounded parameter setters are sufficient

## Trade-offs

**Pros:**
- Gives users and reviewers time to inspect bundled changes
- Keeps immutable systems upgradeable through explicit authority grants
- Makes each governance action contract auditable as a unit

**Cons:**
- A malicious spell is still powerful after the delay
- Spell deployment and manifest review become governance-critical
- Cancellation and emergency paths need their own authority design

## How It Works

Governance schedules a spell contract, waits a delay, then grants it the authority needed to execute the reviewed changes.

```solidity
function scheduleSpell(address spell) external onlyGovernance {
    eta[spell] = block.timestamp + delay;
}

function cast(address spell) external {
    require(block.timestamp >= eta[spell], "delay");
    _grantAuthority(spell);
    ISpell(spell).execute();
    _revokeAuthority(spell);
}
```

## Key Points

- Publish a manifest of targets, selectors, parameters, and expected post-state.
- Let governance cancel scheduled spells before activation.
- Keep emergency pause or guardian authority separate from spell execution.
- Avoid granting persistent wildcard authority to spell contracts.
- Test delay, cancellation, one-shot execution, and failed-spell cleanup.

## Source Evidence

- Centrifuge liquidity pools root contract schedules and relies on spell-style authority for admin changes.
- Guardian pause behavior is separate from scheduled admin spell execution.
- Integration tests cover delay, cancel, and deploy-time authority setup.

## Related Patterns

- [Bounded Timelocked Parameter Change](./pattern-bounded-timelocked-parameter-change.md)
- [Break-Glass Risk Limiter](./pattern-break-glass-risk-limiter.md)
- [Governance as Arbitrary Execution](../../ANTIPATTERNS.md#governance-as-arbitrary-execution)
