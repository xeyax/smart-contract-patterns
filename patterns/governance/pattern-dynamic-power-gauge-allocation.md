# Dynamic-Power Gauge Allocation

> Store user gauge preferences as basis-point weights while deriving effective gauge votes from current voting power.

## Metadata

| Property | Value |
|----------|-------|
| Category | governance |
| Tags | governance, gauges, voting-power, rewards, allocation |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Users allocate changing voting power across gauges or reward nodes
- Preferences should persist while user voting power accrues or decays
- Gauge totals should reflect the latest effective voting power
- Allocations can be represented as percentages or basis points

## Avoid When

- Gauge votes must be fixed snapshots at vote time
- Gauge total recomputation would require unbounded on-chain iteration
- Users can allocate more than 100% of their voting power
- Gauge rewards cannot tolerate delayed updates after voting-power changes

## Trade-offs

**Pros:**
- Users do not need to revote every time voting power changes
- Basis-point preferences are compact and easy to reason about
- Gauge totals track current governance weight rather than stale snapshots

**Cons:**
- Aggregate recomputation can become expensive without bounds or pagination
- Voting-power changes can shift gauge totals outside explicit vote calls
- Reward accounting needs clear timing semantics around pending votes

## How It Works

Store each user's allocation weights in basis points. Effective votes for a
gauge are computed from the user's current voting power multiplied by the stored
allocation.

```solidity
function effectiveGaugeVotes(address user, address gauge) public view returns (uint256) {
    uint256 power = votingPower.balanceOf(user);
    return power * userGaugeBps[user][gauge] / BPS;
}

function vote(address[] calldata gauges, uint16[] calldata bps) external {
    require(_sum(bps) <= BPS, "overallocated");
    _storeAllocation(msg.sender, gauges, bps);
    _refreshGaugeTotals(msg.sender, gauges);
}
```

If aggregate gauge totals are used on-chain, update affected gauges incrementally
or through bounded public maintenance rather than looping all voters.

## Implementation

- Enforce a total allocation cap, usually 10,000 basis points.
- Define whether pending or claimable voting power participates in gauge totals.
- Keep per-gauge aggregation bounded, cached, or cursor-driven.
- Emit allocation changes with old and new weights.
- Test voting-power accrual, vote updates, over-allocation, zero-power users, and voter-list growth.

## Source Evidence

- BENQI's `GaugeController` stores user allocation weights in basis points and derives node votes from current and pending veQI balances in `/private/tmp/defillama-source/benqi-fi__BENQI-Smart-Contracts/veQI/GaugeController.sol`.
- BENQI's implementation also illustrates the risk of aggregating node voters with loops, which should be bounded or kept off critical on-chain paths.

## Real-World Examples

- BENQI veQI gauges let users allocate voting power across nodes while effective votes follow dynamic veQI power.

## Related Patterns

- [Capped Linear Voting Escrow](./pattern-capped-linear-voting-escrow.md)
- [Lazy Reward Index](../rewards/pattern-lazy-reward-index.md)
- [Unbounded Iteration](../../ANTIPATTERNS.md#unbounded-iteration)

## References

- BENQI veQI gauge controller.
