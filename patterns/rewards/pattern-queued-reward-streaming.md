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

## Source Evidence

- Convex uses permissioned reward distributors and carries leftover rewards into new reward rates when streams are refilled before period end.
- Convex proxy harvest flows claim external rewards and split fees through registry-configured recipients.

## Related Patterns

- [High-Water Mark Fee](../vaults/pattern-high-water-mark-fee.md) - NAV-denominated performance fee
- [Dynamic Premium](../vaults/pattern-dynamic-premium.md) - user operation fees
- [Lazy Reward Index](./pattern-lazy-reward-index.md) - per-user reward accrual without iteration
- [Delayed Cumulative Merkle Claims](./pattern-delayed-cumulative-merkle-claims.md) - off-chain reward allocation with delayed root activation
