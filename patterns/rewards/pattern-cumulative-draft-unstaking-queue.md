# Cumulative Draft Unstaking Queue

> Represent delayed unstaking claims as cumulative drafts so users can withdraw prefixes without iterating every pending exit.

## Metadata

| Property | Value |
|----------|-------|
| Category | rewards |
| Tags | rewards, staking, unstaking, queue, cumulative-accounting |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Stakers must wait before withdrawn stake becomes claimable
- Users can create multiple unstaking requests
- Withdrawals should claim all matured requests up to a cursor
- Slashing or seizure can reset stake and draft accounting by era

## Avoid When

- Each unstake request must be individually transferable or cancellable
- The queue must be globally FIFO across all users
- The protocol cannot tolerate per-user array or checkpoint state

## Trade-offs

**Pros:**
- Avoids looping over all users
- Lets each user withdraw matured prefixes efficiently
- Era resets make full seizure or slashing easier to reason about

**Cons:**
- More complex than one cooldown timestamp
- Requires careful cursor and era handling
- Partial withdrawals and rounding need explicit tests

## How It Works

Store each draft as a cumulative amount at an available-at time:

```solidity
struct Draft {
    uint256 cumulativeAmount;
    uint64 availableAt;
}

mapping(address => Draft[]) public drafts;
mapping(address => uint256) public firstUnwithdrawnDraft;

function unstake(uint256 amount) external {
    uint256 cumulative = amount + _lastDraftAmount(msg.sender);
    drafts[msg.sender].push(Draft(cumulative, uint64(block.timestamp + delay)));
}
```

To withdraw, find the last matured draft, subtract the already-withdrawn cumulative amount, and advance the cursor.

## Implementation

```solidity
function withdraw(uint256 endId) external {
    require(drafts[msg.sender][endId - 1].availableAt <= block.timestamp, "not ready");
    uint256 start = firstUnwithdrawnDraft[msg.sender];
    uint256 previous = start == 0 ? 0 : drafts[msg.sender][start - 1].cumulativeAmount;
    uint256 amount = drafts[msg.sender][endId - 1].cumulativeAmount - previous;
    firstUnwithdrawnDraft[msg.sender] = endId;
    _transferStake(msg.sender, amount);
}
```

### Key Points

- Use cumulative amounts so prefix withdrawal is O(1) after selecting `endId`.
- Bound or make searchable the matured-draft cursor.
- Reset eras explicitly after full seizure or stake reset.
- Test multiple unstakes, partial prefix withdrawals, and full-era reset.

## Source Evidence

- Reserve Protocol `StRSR` tracks delayed unstaking drafts with cumulative values, `beginEra`, `beginDraftEra`, and seizure reset paths in `/private/tmp/defillama-source/reserve-protocol__protocol/contracts/p1/StRSR.sol`.
- Reserve tests cover multiple unstakes, withdrawals, full seizure, and era resets in `/private/tmp/defillama-source/reserve-protocol__protocol/test/ZZStRSR.test.ts`.

## Real-World Examples

- Reserve Protocol stRSR - delayed unstaking drafts use cumulative queues and eras.

## Related Patterns

- [Timelock on Shares](../vaults/pattern-timelock-shares.md)
- [Lazy Reward Index](./pattern-lazy-reward-index.md)
- [Withdrawal Queue Starvation](../../ANTIPATTERNS.md#withdrawal-queue-starvation)

## References

- See Source Evidence.
