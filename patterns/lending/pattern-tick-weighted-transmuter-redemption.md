# Tick-Weighted Transmuter Redemption

> Redeem synthetic debt deposits into underlying by advancing active ticks and accumulated weights instead of iterating every depositor.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, redemption, synthetic, transmuter, ticks |
| Complexity | High |
| Gas Efficiency | High |
| Audit Risk | High |

## Use When

- Users deposit synthetic assets into a redemption queue for future underlying
- Underlying arrives over time from harvests, buffers, or repayments
- Redemption priority can be represented as ticks or ordered buckets
- The protocol must avoid per-user iteration when underlying is distributed

## Avoid When

- Every depositor must receive immediate pro-rata settlement
- Queue priority cannot be encoded as ordered buckets
- Underlying losses or pauses can make the redemption weight ambiguous
- Users need transferable claim tokens rather than account-local deposits

## Trade-offs

**Pros:**
- Makes large redemption queues gas-bounded
- Preserves deterministic priority through active ticks
- Lets claims be settled lazily from accumulated weights

**Cons:**
- Tick math and boundary conditions are easy to get wrong
- Users must understand queue priority and partial redemption
- Pauses or buffer shortages can still affect exit liveness

## How It Works

Deposits enter the current or selected tick. When underlying becomes available,
the transmuter advances accumulated weights and moves through ticks:

```solidity
function deposit(uint256 amount) external {
    uint256 tick = currentTick;
    positions[msg.sender][tick] += amount;
    totalAtTick[tick] += amount;
}

function distributeUnderlying(uint256 amount) external {
    while (amount > 0 && totalAtTick[currentTick] > 0) {
        uint256 fill = min(amount, totalAtTick[currentTick]);
        accumulatedWeight[currentTick] += fill * WAD / totalAtTick[currentTick];
        amount -= fill;
        if (_tickFullyFilled(currentTick)) currentTick++;
    }
}
```

## Implementation

### Key Points

- Store per-account cursors so claims do not scan historical ticks.
- Define exact rounding when a tick is partially filled.
- Keep claim liquidity separate from assets that can be redeployed into strategy risk.
- Test empty ticks, partial tick fills, complete tick rollover, repeated deposits at active tick, and pause/claim interactions.

## Source Evidence

- Alchemix Transmuter V2 tracks active ticks, accumulated weights, deposits, and claims in `/private/tmp/defillama-source/alchemix-finance__v2-foundry/src/TransmuterV2.sol`.
- Alchemix transmuter tests cover redemption and claim behavior in `/private/tmp/defillama-source/alchemix-finance__v2-foundry/test/TransmuterV2.spec.ts`.
- Alchemix TransmuterBuffer keeps redemption liquidity from being redeployed into yield-vault risk in `/private/tmp/defillama-source/alchemix-finance__v2-foundry/src/TransmuterBuffer.sol`.

## Real-World Examples

- Alchemix V2 - transmuter queue redeems synthetic deposits into underlying using tick-weight accounting.

## Related Patterns

- [Height-Interval Redemption Queue](../vaults/pattern-height-interval-redemption-queue.md)
- [Withdrawal Liquidity Buffer](../vaults/pattern-withdrawal-liquidity-buffer.md)
- [Unbounded Iteration](../../ANTIPATTERNS.md#unbounded-iteration)

## References

- See Source Evidence.
