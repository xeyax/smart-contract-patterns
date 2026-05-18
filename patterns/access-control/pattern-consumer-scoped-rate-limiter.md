# Consumer-Scoped Rate Limiter

> Apply token-bucket limits per approved consumer or route so one actor cannot exhaust shared capacity for unrelated flows.

## Metadata

| Property | Value |
|----------|-------|
| Category | access-control |
| Tags | access-control, rate-limit, bucket, consumer, dos |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Multiple protocol components share a constrained operation such as instant redemption, bridge egress, or privileged consumption
- A global cap would let one consumer starve others
- Consumers can be allowlisted and assigned independent capacity
- The operation is high-value enough to justify stateful rate limiting

## Avoid When

- The caller identity cannot be bound to a meaningful consumer or route
- Capacity should be completely fungible across all consumers
- Bucket refill rules are too complex to reason about during incidents

## Trade-offs

**Pros:**
- Limits Sybil and denial-of-service pressure from one consumer path
- Makes capacity allocation explicit and monitorable
- Keeps emergency throttling localized

**Cons:**
- Requires governance to size and maintain per-consumer limits
- Misconfigured consumers can strand unused capacity
- Bucket math must be tested around refill boundaries and partial use

## How It Works

Each consumer is assigned to a bucket with its own capacity, refill rate, and authorization:

```solidity
struct Bucket {
    uint256 capacity;
    uint256 available;
    uint256 refillPerSecond;
    uint256 lastUpdated;
}

mapping(bytes32 => Bucket) public buckets;
mapping(address => bytes32) public consumerBucket;

function consume(address consumer, uint256 amount) external onlyAuthorizedConsumer(consumer) {
    bytes32 id = consumerBucket[consumer];
    Bucket storage bucket = buckets[id];
    _refill(bucket);
    require(bucket.available >= amount, "rate limited");
    bucket.available -= amount;
}
```

Consumers can share a bucket intentionally, but that grouping should be an explicit risk decision.

## Key Points

- Authorize both the caller and the consumer bucket.
- Keep bucket ids stable and visible in events.
- Test independent buckets, shared buckets, refill boundaries, and over-capacity attempts.
- Do not let untrusted users create unlimited consumers to bypass the limit.
- Pair with a break-glass role that can lower or zero a compromised consumer's bucket.

## Source Evidence

- Ether.fi uses bucket ids plus consumer allowlists to isolate rate-limited usage and tests independent bucket accounting and consumer isolation.

## Related Patterns

- [Break-Glass Risk Limiter](./pattern-break-glass-risk-limiter.md)
- [Withdrawal Liquidity Buffer](../vaults/pattern-withdrawal-liquidity-buffer.md)
- [Bridge Custodian Concentration](../../ANTIPATTERNS.md#bridge-custodian-concentration)
