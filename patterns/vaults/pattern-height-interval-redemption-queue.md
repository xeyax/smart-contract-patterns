# Height-Interval Redemption Queue

> Match redemption requests against cumulative withdrawal intervals so claims can be resolved by interval height instead of scanning the full queue.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, redemption, queue, interval, liquid-staking |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Redemptions are satisfied by discrete withdrawal events or external unstaking intervals
- The protocol must support many pending requests without scanning all of them on claim
- Claims can be matched by cumulative request and withdrawal heights
- Partial claims and skipped claims need deterministic status reporting

## Avoid When

- The queue is small enough for direct FIFO processing
- Withdrawal events cannot be ordered or assigned cumulative capacity
- Users must receive one uniform price across an entire epoch
- The protocol cannot test boundary cases for partial interval overlap

## Trade-offs

**Pros:**
- Resolves claims against compact interval checkpoints
- Supports partial fulfillment without mutating the whole queue
- Gives off-chain indexers deterministic matching data

**Cons:**
- Harder to audit than simple FIFO queues
- Off-by-one interval errors can misallocate claim capacity
- Requires explicit handling for already claimed and out-of-bounds requests

## How It Works

Each request records its cumulative redemption height:

```solidity
struct RedeemRequest {
    address owner;
    uint256 startHeight;
    uint256 endHeight;
    bool claimed;
}
```

Each withdrawal event records cumulative capacity:

```solidity
struct WithdrawalEvent {
    uint256 startHeight;
    uint256 endHeight;
    uint256 assets;
}
```

Claiming matches overlap between request intervals and withdrawal intervals:

```solidity
function claim(uint256 requestId, uint256[] calldata eventIds) external {
    RedeemRequest storage r = requests[requestId];
    require(!r.claimed, "claimed");

    uint256 claimable;
    for (uint256 i; i < eventIds.length; i++) {
        claimable += _overlapValue(r, withdrawalEvents[eventIds[i]]);
    }

    require(claimable != 0, "not satisfied");
    r.claimed = true;
    _pay(r.owner, claimable);
}
```

For large histories, off-chain helpers can suggest event ids and a bounded search depth, but the on-chain claim must reject mismatched intervals.

## Implementation

### Key Points

- Store cumulative request and withdrawal heights, not only per-request amounts.
- Make overlap calculation deterministic and fuzz exact boundary values.
- Return explicit statuses for fully claimed, partially claimed, skipped, unsatisfied, out-of-bounds, and already-claimed requests.
- Bound claim input size or depth so a single claim cannot become uncallable.
- Mark claimed or partially claimed state before paying.
- Keep event capacity and request intervals immutable after they become claimable.

## Source Evidence

- Liquid Collective `RedeemManagerV1` exposes claim functions that match redeem request ids to withdrawal event ids, return per-request claim statuses, and include helper logic for finding matching withdrawal events in `/private/tmp/defillama-source/liquid-collective__liquid-collective-protocol/natspec/RedeemManagerV1.md`.
- The same NatSpec documents full, partial, skipped, not-satisfied, out-of-bounds, and already-claimed cases, making interval matching a reusable queue design rather than a simple FIFO transfer.

## Real-World Examples

- Liquid Collective - liquid-staking redemption manager with cumulative interval matching between redeem requests and withdrawal events.

## Related Patterns

- [Async Deposit/Withdrawal](./pattern-async-deposit.md)
- [Withdrawal Liquidity Buffer](./pattern-withdrawal-liquidity-buffer.md)
- [Vault Fairness Requirements](./req-vault-fairness.md)

## References

- See Source Evidence.
