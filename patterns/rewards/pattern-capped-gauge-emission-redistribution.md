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

- Aerodrome Slipstream caps gauge emissions in `/private/tmp/defillama-source/aerodrome-finance__slipstream/contracts/gauge/CLGauge.sol` through `notifyRewardAmount`.
- Aerodrome factory cap controls are in `contracts/gauge/CLGaugeFactory.sol` through `setEmissionCap` and `calculateMaxEmissions`.
- Aerodrome redistributes excess through `contracts/gauge/Redistributor.sol` and `_redistribute`.
- Velodrome V2 killed gauges reject new deposits, preserve withdrawals, and redirect pending or future emissions in `/private/tmp/defillama-source/velodrome-finance__contracts/contracts/Gauge.sol` and `contracts/Voter.sol`.
- Velodrome Superchain leaf gauges and voters route cross-chain emissions and kill-state behavior through `/private/tmp/defillama-source/velodrome-finance__superchain-contracts/src/gauges/LeafGauge.sol` and `/private/tmp/defillama-source/velodrome-finance__superchain-contracts/src/voter/LeafVoter.sol`.
- Aerodrome V1 returns killed-gauge claimable emissions to the minter and tests killed-gauge distribution behavior in `/private/tmp/defillama-source/aerodrome-finance__contracts/contracts/Voter.sol` and `/private/tmp/defillama-source/aerodrome-finance__contracts/test/Voter.t.sol`.

## Real-World Examples

- Aerodrome Slipstream caps concentrated-liquidity gauge emissions and redistributes excess rewards.

## Related Patterns

- [Range Liquidity Reward Index](./pattern-range-liquidity-reward-index.md)
- [Checkpointed Epoch Reward Buckets](./pattern-checkpointed-epoch-reward-buckets.md)
- [Queued Reward Streaming](./pattern-queued-reward-streaming.md)

## References

- Aerodrome Slipstream gauge and redistributor contracts.
