# Dynamic-Power Gauge Allocation

> Store user gauge preferences as basis-point weights while deriving effective gauge votes from current voting power.

## Metadata

| Property | Value |
|----------|-------|
| Category | governance |
| Tags | governance, gauge, voting-power, rewards, allocation |
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

Vote-escrow gauge controllers can schedule gauge weight changes by week and use
decaying user slopes from lock-end voting power. In that variant, user votes
should be capped at 10,000 bps, revotes should have a delay, and gauges should
checkpoint slope changes by epoch rather than scanning all voters.

## Implementation

- Enforce a total allocation cap, usually 10,000 basis points.
- Define whether pending or claimable voting power participates in gauge totals.
- Keep per-gauge aggregation bounded, cached, or cursor-driven.
- For decaying voting escrow, schedule gauge weights by epoch and checkpoint
  slope changes at lock ends.
- Enforce revote delays so users cannot rapidly redirect the same voting power.
- Emit allocation changes with old and new weights.
- Test voting-power accrual, vote updates, over-allocation, zero-power users, and voter-list growth.
- For veNFT systems, test managed-lock deposit and withdrawal as gauge voting state changes, not only as escrow transfers.
- If utilization changes allocation points, checkpoint pool rewards before applying the utilization-derived multiplier.

## Source Evidence

- BENQI's `GaugeController` stores user allocation weights in basis points and derives node votes from current and pending veQI balances in [`veQI/GaugeController.sol`](https://github.com/benqi-fi/BENQI-Smart-Contracts/blob/e0cfd244726719dfe027c9740878d64d1cad98f2/veQI/GaugeController.sol).
- BENQI's implementation also illustrates the risk of aggregating node voters with loops, which should be bounded or kept off critical on-chain paths.
- Curve DAO GaugeController schedules weekly gauge weights, applies decaying
  slopes, checks lock end, enforces a 10-day revote delay, and caps user power at
  10,000 bps in [`contracts/GaugeController.vy:188-285`](https://github.com/curvefi/curve-dao-contracts/blob/fa127b1cb7bf83e4f3d605f7244b7b4ed5ebe053/contracts/GaugeController.vy#L188-L285),
  [`contracts/GaugeController.vy:345-380`](https://github.com/curvefi/curve-dao-contracts/blob/fa127b1cb7bf83e4f3d605f7244b7b4ed5ebe053/contracts/GaugeController.vy#L345-L380),
  and [`contracts/GaugeController.vy:485-553`](https://github.com/curvefi/curve-dao-contracts/blob/fa127b1cb7bf83e4f3d605f7244b7b4ed5ebe053/contracts/GaugeController.vy#L485-L553).
- Aerodrome V1 normalizes gauge vote weights by current veNFT balance, caps vote count, and updates managed lock voting state in [`contracts/Voter.sol`](https://github.com/aerodrome-finance/contracts/blob/1ba30815bba620f7e9faa34769ffd00c214c9b82/contracts/Voter.sol).
- Premia Mining combines pool votes with utilization-rate multipliers to compute allocation points in [`contracts/mining/PremiaMining.sol`](https://github.com/premiafinance/premia-contracts/blob/0ed54a91c6b69b17a8cc9d6208aadb442218a07f/contracts/mining/PremiaMining.sol).

## Real-World Examples

- BENQI veQI gauges let users allocate voting power across nodes while effective votes follow dynamic veQI power.

## Related Patterns

- [Capped Linear Voting Escrow](./pattern-capped-linear-voting-escrow.md)
- [Lazy Reward Index](../rewards/pattern-lazy-reward-index.md)
- [Unbounded Iteration](../../ANTIPATTERNS.md#unbounded-iteration)

## References

- BENQI veQI gauge controller.
