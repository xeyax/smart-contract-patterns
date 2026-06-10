# Capped Gauge Emission Redistribution

> Cap per-gauge reward emissions and redirect excess into an epoch-snapshotted redistributor.

## Metadata

| Property | Value |
|----------|-------|
| Category | rewards |
| Tags | gauge, emissions, cap, redistribution, epoch |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Governance or voters allocate emissions across gauges
- Individual gauges need maximum reward flow limits
- Excess emissions should remain in the reward system instead of being trapped
- Killed or inactive gauges should not continue receiving redistributed rewards

## Avoid When

- Gauge weights are already hard-capped before funding
- Excess rewards should be burned or returned directly to treasury
- Epoch accounting cannot snapshot cap usage and remaining capacity

## Trade-offs

**Pros:**
- Prevents one gauge from receiving more than configured maximum emissions
- Preserves reward budget by reallocating capped excess
- Gives governance a clear safety limit without discarding rewards

**Cons:**
- Redistribution can be gamed if remaining-cap snapshots are stale
- Killed gauges and cap changes require careful epoch handling
- More moving parts than direct gauge notification

## How It Works

When a gauge receives rewards, it accepts up to its epoch cap. Any excess is sent
to a redistributor that snapshots remaining eligible capacity and routes rewards
to gauges that can still accept them.

```solidity
function notifyRewardAmount(uint256 amount) external {
    uint256 cap = gaugeFactory.maxEmissions(address(this), currentEpoch());
    uint256 accepted = min(amount, cap - emissionsThisEpoch);
    emissionsThisEpoch += accepted;

    _queueReward(accepted);
    if (amount > accepted) {
        redistributor.redistribute(amount - accepted);
    }
}
```

## Implementation

- Snapshot cap usage by epoch.
- Exclude killed or disabled gauges from redistributed rewards.
- Recompute remaining capacity before accepting redistributed amounts.
- Bound redistribution iteration or process it through cursors.
- Test cap changes, killed gauges, no-capacity epochs, and repeated redistributions.
- If governance can kill a gauge, reject new deposits, preserve withdrawals, and return pending or future emissions to the minter or redistributor instead of trapping rewards in the dead gauge.
- For cross-chain gauge systems, define whether root-chain emissions are escrowed, bridged, or returned when a leaf gauge is killed or cannot receive messages.

## Source Evidence

- Aerodrome Slipstream caps gauge emissions in [`contracts/gauge/CLGauge.sol`](https://github.com/aerodrome-finance/slipstream/blob/f8717faaae6e6717db3c8e3850149c01a79c0603/contracts/gauge/CLGauge.sol) through `notifyRewardAmount`.
- Aerodrome factory cap controls are in `contracts/gauge/CLGaugeFactory.sol` through `setEmissionCap` and `calculateMaxEmissions`.
- Aerodrome redistributes excess through `contracts/gauge/Redistributor.sol` and `_redistribute`.
- Velodrome V2 killed gauges reject new deposits, preserve withdrawals, and redirect pending or future emissions in [`contracts/Gauge.sol`](https://github.com/velodrome-finance/contracts/blob/b3065d8b6702b14b094f9f6046b752cc9f78c43b/contracts/Gauge.sol) and `contracts/Voter.sol`.
- Velodrome Superchain leaf gauges and voters route cross-chain emissions and kill-state behavior through [`src/gauges/LeafGauge.sol`](https://github.com/velodrome-finance/superchain-contracts/blob/c93c466a2fcd1fd9dc79ba569f6b81c42bb50d61/src/gauges/LeafGauge.sol) and [`src/voter/LeafVoter.sol`](https://github.com/velodrome-finance/superchain-contracts/blob/c93c466a2fcd1fd9dc79ba569f6b81c42bb50d61/src/voter/LeafVoter.sol).
- Aerodrome V1 returns killed-gauge claimable emissions to the minter and tests killed-gauge distribution behavior in [`contracts/Voter.sol`](https://github.com/aerodrome-finance/contracts/blob/1ba30815bba620f7e9faa34769ffd00c214c9b82/contracts/Voter.sol) and [`test/Voter.t.sol`](https://github.com/aerodrome-finance/contracts/blob/1ba30815bba620f7e9faa34769ffd00c214c9b82/test/Voter.t.sol).

## Real-World Examples

- Aerodrome Slipstream caps concentrated-liquidity gauge emissions and redistributes excess rewards.

## Related Patterns

- [Range Liquidity Reward Index](./pattern-range-liquidity-reward-index.md)
- [Checkpointed Epoch Reward Buckets](./pattern-checkpointed-epoch-reward-buckets.md)
- [Queued Reward Streaming](./pattern-queued-reward-streaming.md)

## References

- Aerodrome Slipstream gauge and redistributor contracts.
