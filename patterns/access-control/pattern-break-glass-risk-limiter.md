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
- For AMMs, operation modes should be separated by risk: stopping new deposits, swaps, and order placement does not automatically imply stopping withdrawals, cancel/settle maintenance, or other exit-enabling paths.
- Emergency risk-reduction setters should not require fresh oracle reads unless the reduced state itself depends on that price; stale oracle liveness should not block containment.
- Treat bypass-threshold increases as risk-increasing even when small transfers bypass monitoring; use one-shot guardians, separate roles, or governance for increases, while allowing monotonic threshold decreases through the limiter.

## Source Evidence

- Ethena separates emergency risk-limiting powers from broader admin powers so a limiter can reduce exposure during a custody or mint/redeem incident without being able to restore full capacity alone.
- Raydium AMM exposes operation-mode gates for deposit, withdraw, swap, and orderbook behavior; the reusable lesson is the scoped mode matrix, not immediate owner-controlled parameter changes.
- Euler V2 documentation shows that requiring fresh pull-oracle reads for a risk-reducing LTV setter can block emergency borrow-LTV zeroing and push operators toward unsafe temporary oracle stubs.
- Lombard's bascule controls distinguish replay-monitor bypass threshold increases from monotonic decreases, including one-shot authority for threshold increases.

## Related Patterns

- [Selector-Scoped Authority](./pattern-selector-scoped-authority.md)
- [Two-Step Authority Handoff](./pattern-two-step-authority-handoff.md)
- [Oracle Staleness Risk](../oracles/risk-oracle-staleness.md)
- [Unrestricted Admin](../../ANTIPATTERNS.md#unrestricted-admin)
