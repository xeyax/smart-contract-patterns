# Risk-Bucketed Position Ticks

> Group debt positions by risk-ratio buckets so redemptions, rebalances, and liquidations can process the riskiest buckets first.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, cdp, ticks, liquidation, redemption, risk |
| Complexity | High |
| Gas Efficiency | High |
| Audit Risk | High |

## Use When

- Positions can be ordered by a discrete debt ratio, collateral ratio, or similar risk metric
- Liquidations or redemptions should start with the worst-risk positions
- The active position set is too large for per-position sorting on every update
- Lazy bucket movement can be proven to preserve redemption/liquidation priority

## Avoid When

- The risk metric changes continuously and cannot be bucketed safely
- Bucket traversal can become unbounded in normal operations
- Dust positions can fill many buckets and block useful work
- Users can avoid repricing by staying in stale buckets

## Trade-offs

**Pros:**
- Reduces sorting overhead by grouping nearby-risk positions
- Gives liquidation and redemption paths deterministic priority
- Can combine lazy movement with bounded scans

**Cons:**
- Tick movement and dust behavior are complex to audit
- Bucket boundaries can create edge-case incentives
- Worst-bucket scans still need hard limits or public batching

## How It Works

Map each position to a risk bucket. Bucket-level metadata tracks aggregate debt,
collateral, and links to neighboring non-empty buckets. Risk-changing operations
move a position between buckets or lazily update bucket ratios.

```solidity
function updatePosition(uint256 id, uint256 collateral, uint256 debt) external {
    uint256 oldTick = positions[id].tick;
    uint256 newTick = _riskTick(collateral, debt);

    if (oldTick != newTick) {
        _removeFromTick(oldTick, id);
        _insertIntoTick(newTick, id);
    }

    positions[id] = Position({collateral: collateral, debt: debt, tick: newTick});
}

function liquidateWorst(uint256 maxTicks) external {
    uint256 tick = worstTick;
    for (uint256 i; i < maxTicks && _isUnsafe(tick); i++) {
        _liquidateOrRebalanceTick(tick);
        tick = _nextWorstTick(tick);
    }
}
```

## Implementation

- Define the tick formula and rounding direction explicitly.
- Bound per-call tick traversal and position processing.
- Apply minimum debt or dust rules so tiny positions cannot fill buckets cheaply.
- Keep lazy movement monotonic or prove when stale buckets remain safe.
- Test exact-boundary positions, dust, empty-bucket removal, worst-tick scans, and ratio propagation.

## Source Evidence

- fx Protocol groups positions by debt-ratio ticks, scans high-risk ticks for redemption/rebalance/liquidation, applies dust handling, and lazily propagates ratio movement through tick nodes in `/private/tmp/defillama-source/AladdinDAO__fx-protocol-contracts/contracts/core/pool/BasePool.sol` and `contracts/core/pool/TickLogic.sol`.
- fx Protocol tests cover tick-driven pool manager behavior in `/private/tmp/defillama-source/AladdinDAO__fx-protocol-contracts/test/core/PoolManager.spec.ts`.

## Real-World Examples

- fx Protocol uses debt-ratio tick buckets to prioritize redemptions, rebalances, and liquidations.

## Related Patterns

- [Hint-Assisted Risk-Ordered Position List](./pattern-hint-assisted-risk-ordered-position-list.md)
- [Risk-Priority Liquidation Sequencing](./pattern-risk-priority-liquidation-sequencing.md)
- [Unbounded Iteration](../../ANTIPATTERNS.md#unbounded-iteration)

## References

- fx Protocol pool tick logic.
