# Break-Glass Risk Limiter

> Give an emergency role narrowly scoped powers to reduce risk limits or disable risky routes without granting the power to re-enable them.

## Metadata

| Property | Value |
|----------|-------|
| Category | access-control |
| Tags | access-control, emergency, guardian, limits, containment |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- Operators need to react faster than governance during suspected compromise or market stress
- The emergency action should only reduce protocol exposure
- Normal governance or admin should remain responsible for restoring capacity
- Mint, redeem, bridge, route, or custodian limits can be bounded independently

## Avoid When

- The emergency role can move funds or set arbitrary addresses
- The same role can both disable and re-enable a risky path without delay
- There is no monitoring or playbook for using the role

## Trade-offs

**Pros:**
- Reduces blast radius of emergency authority
- Lets risk teams contain incidents without full admin keys
- Makes emergency actions easy to audit because they are monotonic

**Cons:**
- A malicious limiter can temporarily reduce protocol availability
- Governance must have a reliable path to restore healthy limits
- Limit semantics need careful design around pending orders and withdrawals

## How It Works

Separate risk-reducing operations from risk-increasing operations:

```solidity
function reduceMintLimit(address route, uint256 newLimit) external onlyRiskLimiter {
    require(newLimit <= mintLimit[route], "limit can only decrease");
    mintLimit[route] = newLimit;
}

function restoreMintLimit(address route, uint256 newLimit) external onlyGovernance {
    require(newLimit <= maxMintLimit[route], "above cap");
    mintLimit[route] = newLimit;
}
```

The emergency role can revoke routes, lower caps, or zero allowances. It cannot add new routes, increase caps, upgrade code, rescue assets, or assign itself broader permissions.

## Key Points

- Make every emergency function monotonic in the safe direction.
- Keep restoration behind governance, timelock, multisig, or a different admin quorum.
- Emit events that include old and new limits for monitoring.
- Define whether pending orders use the old limit, new limit, or must be cancelled.
- Test that the emergency role cannot regain capacity through alternate setters.

## Source Evidence

- Ethena separates emergency risk-limiting powers from broader admin powers so a limiter can reduce exposure during a custody or mint/redeem incident without being able to restore full capacity alone.

## Related Patterns

- [Selector-Scoped Authority](./pattern-selector-scoped-authority.md)
- [Two-Step Authority Handoff](./pattern-two-step-authority-handoff.md)
- [Unrestricted Admin](../../ANTIPATTERNS.md#unrestricted-admin)
