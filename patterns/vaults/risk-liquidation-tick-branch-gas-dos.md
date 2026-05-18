# Liquidation Tick Branch Gas DoS

> Liquidation and absorb paths can become too expensive when they must walk fragmented tick, branch, or position maps before restoring solvency.

## Metadata

| Property | Value |
|----------|-------|
| Type | Risk Description |
| Category | vaults |
| Tags | liquidation, ticks, gas, dos, solvency |

## Applies When

- Liquidations iterate through price ticks, branch lists, or position buckets
- Users can fragment debt or collateral across many small positions
- The last position in a tick or branch needs extra cleanup logic
- Solvency restoration depends on the liquidation finishing within gas limits

## Risk Vectors

### Fragmented Tick Traversal

If liquidation walks tick maps until enough debt is absorbed, an attacker can create many thin ticks or force traversal across sparse branches.

### Last-Position Cleanup

Special handling for the last user in a tick can add branches, storage clears, or rebalancing steps exactly when liquidation already has high gas pressure.

### Absorb Backlog

If bad debt or absorbed collateral accumulates in branch chains, keeper operations can become unprofitable or impossible during stress.

## Mitigations

- Bound liquidation work per transaction and expose continuation state.
- Enforce minimum economic position size per tick or branch.
- Add keeper incentives that scale with traversal cost.
- Fuzz fragmented positions, last-position branches, and near-gas-limit liquidation.
- Provide emergency partial liquidation or absorb paths that reduce risk without full traversal.

## Source Evidence

- Fluid vault liquidation and absorb flows walk tick and branch structures, with source comments and tests around last-user and branch traversal behavior.

## Related Patterns

- [Dust-Aware Liquidation Cap](../lending/pattern-dust-aware-liquidation-cap.md)
- [Risk-Priority Liquidation Sequencing](../lending/pattern-risk-priority-liquidation-sequencing.md)
- [Tick Crossing Gas DoS](../liquidity/risk-tick-crossing-gas-dos.md)
