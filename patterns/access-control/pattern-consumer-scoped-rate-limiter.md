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

### Pairwise Bridge Route Variant

For cross-chain bridges, the consumer key may need to include both source and destination route:

```solidity
bytes32 bucketId = keccak256(abi.encode(srcChainId, dstChainId, asset, direction));
_consume(bucketId, amount);
```

This prevents inbound liquidity for one route from consuming outbound capacity for another route unless the shared bucket is intentional.

### Route-Key Allowlist Variant

Unset bucket keys can fail closed, making the rate-limit key double as an integration allowlist. In that model, derive keys from the operation and the relevant asset, destination, pool, domain, or recipient rather than from caller identity alone:

```solidity
bytes32 key = keccak256(abi.encode("TRANSFER_ASSET", asset, destination));
_consume(key, amount); // reverts when key has zero max capacity
```

Reverse flows need an explicit policy. Restore capacity only when the reverse action truly returns the same risk capacity; otherwise consume a separate bucket for the reverse direction.

### Destination-Scoped OFT Variant

Omnichain tokens can throttle outbound transfers by destination endpoint before
debiting local balances:

```solidity
bytes32 key = keccak256(abi.encode(token, dstEndpointId));
_consume(key, amountLD);
_debit(from, amountLD, minAmountLD, dstEndpointId);
```

This prevents one destination from consuming capacity intended for another.
Normalize dust before the limit check if the bridge converts between local and
shared decimals.

## Key Points

- Authorize both the caller and the consumer bucket.
- Keep bucket ids stable and visible in events.
- Test independent buckets, shared buckets, refill boundaries, and over-capacity attempts.
- Do not let untrusted users create unlimited consumers to bypass the limit.
- Pair with a break-glass role that can lower or zero a compromised consumer's bucket.
- For bridges, distinguish inbound/outbound direction and source/destination pair in the bucket key when route isolation matters.
- Use unset-key fail-closed behavior as an allowlist only when missing configuration is visible and tested.
- Bind route keys to operation plus asset, destination, pool, domain, or recipient.
- For balance-delta based limiters, reject untrusted hooks or callbacks that can manipulate measured balances during the external call.
- Bridge outflows may need destination daily caps, per-transfer min/max, per-user daily caps, and per-user attempt caps, with dust normalization before limit checks.
- Define whether pause time refills capacity. If accumulated capacity during a pause would surprise operators, reset or checkpoint bucket timestamps on unpause.
- For OFT-style bridges, consume destination-scoped capacity before burning or locking local supply.
- For XERC20-style bridge minters, use a midpoint or replenishing buffer per bridge so one bridge cannot exhaust mint/burn capacity intended for other routes.

## Source Evidence

- Ether.fi uses bucket ids plus consumer allowlists to isolate rate-limited usage and tests independent bucket accounting and consumer isolation.
- Veda's LayerZero teller path applies pairwise inbound and outbound rate limits so bridge capacity is isolated by route.
- Spark ALM uses route keys as implicit allowlists, binds limiter keys to operation-specific route fields, restores capacity only for selected reverse flows, and avoids hook-enabled liquidity operations where hooks could change balance-delta measurements.
- Lista OFT combines destination-specific daily caps, per-transfer min/max, per-user daily caps, per-user attempt caps, and dust normalization before debit limit checks.
- USDT0 audit reports discuss route-scoped OFT rate limits and pause-aware refill behavior; this is lower-confidence audit-source evidence because no implementation code was present in the inspected repository.
- Astherus `asBTC` applies transfer-limiter checks from `_debit` before LayerZero OFT debit settlement, with limiter state in [`contracts/oft/TransferLimiter.sol`](https://github.com/astherus-contract/astherus-earn-contract/blob/1472bad4d7267a2c9dbf490b646201ad673e9285/contracts/oft/TransferLimiter.sol) and `contracts/oft/asBTC.sol`.
- Velodrome Superchain restricted XERC20 bridge capacity is implemented in [`src/xerc20/extensions/RestrictedXERC20.sol`](https://github.com/velodrome-finance/superchain-contracts/blob/c93c466a2fcd1fd9dc79ba569f6b81c42bb50d61/src/xerc20/extensions/RestrictedXERC20.sol) and bridge wiring under [`src/bridge`](https://github.com/velodrome-finance/superchain-contracts/blob/c93c466a2fcd1fd9dc79ba569f6b81c42bb50d61/src/bridge).

## Related Patterns

- [Break-Glass Risk Limiter](./pattern-break-glass-risk-limiter.md)
- [Bridge Exit Liveness Requirements](../cross-chain/req-bridge-exit-liveness.md)
- [Withdrawal Liquidity Buffer](../vaults/pattern-withdrawal-liquidity-buffer.md)
- [Bridge Custodian Concentration](../../ANTIPATTERNS.md#bridge-custodian-concentration)
