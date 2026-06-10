# Queued Reward Streaming

> Queue reward tokens from permissioned distributors, carry leftovers forward, and stream rewards over a fixed duration.

## Metadata

| Property | Value |
|----------|-------|
| Category | rewards |
| Tags | rewards, staking, streaming, leftover, fee-split |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Rewards arrive in discrete deposits but should accrue smoothly
- Only approved distributors should fund reward streams
- Existing undistributed rewards should not be overwritten
- Harvested rewards need protocol or adapter fee splitting

## Avoid When

- Rewards should be claimable immediately in full
- Reward token balances can be donated and should not affect accounting
- The distributor set cannot be governed or monitored

## Trade-offs

**Pros:**
- Smooths discrete reward deposits into continuous accrual, removing claim-timing races around large drops.
- Leftover carry-forward preserves undistributed rewards when streams are refilled before period end.
- Distributor allowlist blocks donation-based manipulation of reward rates.
- Streaming over a fixed duration neutralizes the flash-deposit capture that instant payout modes invite.

**Cons:**
- User reward accounting must update before every global rate change; ordering bugs silently corrupt accrued balances.
- Integer division of `amount / rewardsDuration` leaves dust and can round small notifications to a zero rate.
- Frequent re-notification before period end repeatedly dilutes the rate and pushes out `periodFinish`, delaying full distribution.
- Adds governance surface: distributor set, duration changes, and fee splits all need timelocks or monitoring.
- Rewards lag funding by up to the full stream duration — worse UX than immediate claims.

## How It Works

When new rewards arrive before the current period finishes, carry the remaining amount into the new rate:

```solidity
function notifyRewardAmount(address token, uint256 amount) external onlyDistributor {
    RewardData storage r = rewards[token];

    if (block.timestamp >= r.periodFinish) {
        r.rewardRate = amount / rewardsDuration;
    } else {
        uint256 remaining = r.periodFinish - block.timestamp;
        uint256 leftover = remaining * r.rewardRate;
        r.rewardRate = (amount + leftover) / rewardsDuration;
    }

    r.lastUpdateTime = block.timestamp;
    r.periodFinish = block.timestamp + rewardsDuration;
}
```

For harvested reward flows, claim into an adapter first, split fees, then notify the net stream:

```solidity
function harvestAndQueue() external {
    uint256 claimed = _claimExternalRewards();
    uint256 fee = claimed * feeBps / BPS;
    _transfer(feeRecipient, fee);
    _notifyRewardAmount(claimed - fee);
}
```

## Key Points

- Restrict reward notification to approved distributors.
- Update user reward accounting before changing global reward rates.
- Carry leftover undistributed rewards forward.
- Bound reward duration changes through governance or timelock.
- Fee splits should happen before queuing so streamed accounting matches token balance.
- Treat instant distribution as flash-deposit sensitive unless stake duration, caller eligibility, or trigger design prevents same-transaction entry and claim.
- For epoch-governed gauges, end the stream at the next epoch boundary instead of `now + duration`, carry leftovers, reject zero reward rates, and cap the rate by the funded balance.
- Reward liquidation flows should validate sell amount, deadline, fair-price minimums, and fee splits before queueing net rewards into the rewarder.

## Source Evidence

- Convex uses permissioned reward distributors and carries leftover rewards into new reward rates when streams are refilled before period end.
- Convex proxy harvest flows claim external rewards and split fees through registry-configured recipients.
- Reserve staking audit material warns that instant payout modes are vulnerable to flash deposits when reward funding is externally triggerable.
- Velodrome V2 gauges stream rewards until the next epoch boundary, carry leftovers, reject zero rates, and cap reward rate by balance in [`contracts/Gauge.sol`](https://github.com/velodrome-finance/contracts/blob/b3065d8b6702b14b094f9f6046b752cc9f78c43b/contracts/Gauge.sol).
- Tokemak V2 liquidates claimed destination-vault rewards through whitelisted swappers with oracle minimums and queues net proceeds into main rewarders that carry queued rewards forward in [`src/liquidation/LiquidationRow.sol`](https://github.com/Tokemak/v2-core-pub/blob/de163d5a1edf99281d7d000783b4dc8ade03591e/src/liquidation/LiquidationRow.sol) and [`src/rewarders/AbstractRewarder.sol`](https://github.com/Tokemak/v2-core-pub/blob/de163d5a1edf99281d7d000783b4dc8ade03591e/src/rewarders/AbstractRewarder.sol).

## Related Patterns

- [High-Water Mark Fee](../vaults/pattern-high-water-mark-fee.md) - NAV-denominated performance fee
- [Dynamic Premium](../vaults/pattern-dynamic-premium.md) - user operation fees
- [Lazy Reward Index](./pattern-lazy-reward-index.md) - per-user reward accrual without iteration
- [Delayed Cumulative Merkle Claims](./pattern-delayed-cumulative-merkle-claims.md) - off-chain reward allocation with delayed root activation
