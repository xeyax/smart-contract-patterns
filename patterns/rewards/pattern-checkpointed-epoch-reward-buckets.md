# Checkpointed Epoch Reward Buckets

> Allocate newly received rewards into time buckets and let users claim against historical balance checkpoints for each epoch.

## Metadata

| Property | Value |
|----------|-------|
| Category | rewards |
| Tags | rewards, epoch, checkpoints, fee-distribution, claim |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Reward entitlement depends on balances held at epoch boundaries
- User balances are checkpointed or vote-escrowed over time
- Rewards arrive periodically and should be allocated by elapsed time
- Claims can tolerate bounded catch-up work over several epochs

## Avoid When

- Reward tokens are arbitrary fee-on-transfer assets and accounting does not use balance deltas
- Users need continuous per-block accrual instead of epoch buckets
- Zero-supply epochs cannot be handled or recovered
- Catch-up loops cannot be bounded without losing claimability

## How It Works

When new rewards arrive, checkpoint elapsed epochs and distribute the amount into bucketed epoch totals:

```solidity
function checkpointRewards(uint256 maxEpochs) external {
    uint256 received = rewardToken.balanceOf(address(this)) - accountedRewards;
    uint256 processed;

    while (processed < maxEpochs && lastCheckpoint < block.timestamp) {
        uint256 epoch = lastCheckpoint / EPOCH;
        rewardsPerEpoch[epoch] += _portionForEpoch(received, epoch);
        lastCheckpoint += EPOCH;
        processed++;
    }
}
```

Claiming uses the user's historical balance at each epoch start and the total supply checkpoint for that epoch:

```solidity
claim += rewardsPerEpoch[epoch] * balanceAt(user, epochStart) / supplyAt(epochStart);
```

## Key Points

- Bound both reward checkpoint catch-up and user claim loops.
- Define what happens when total supply is zero for an epoch.
- Use exact-transfer curated reward tokens or balance-delta accounting.
- Store user claim cursors so partial claims can resume.
- Test stale checkpoint catch-up, zero-supply epochs, multiple reward arrivals, and partial claims.
- Provide an emergency recovery path for unclaimable or mis-sent rewards.

## Source Evidence

- Stake DAO's `FeeDistributor` distributes fees by epoch, uses historical balance checkpoints for claims, documents zero-supply epoch loss, and bounds both checkpoint and claim loops with integration tests for partial catch-up.

## Related Patterns

- [Lazy Reward Index](./pattern-lazy-reward-index.md)
- [Queued Reward Streaming](./pattern-queued-reward-streaming.md)
- [Balance Delta Transfer Accounting](../token-integration/pattern-balance-delta-transfer-accounting.md)
