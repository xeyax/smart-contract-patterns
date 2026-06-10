# Pairwise Bridge Rate Limits

> Rate-limit bridge flow per source and destination peer so one route cannot drain or flood every other route.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, rate-limit, peer, oft, liveness |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A bridge token has multiple trusted peers or endpoints
- The risk of one remote route should not consume global bridge capacity
- Inbound and outbound flow need independent limits
- Limits should refill predictably over time

## Avoid When

- Bridge capacity must be fully shared across all routes
- Remote peers are not authenticated on-chain
- Governance can raise limits instantly without monitoring or delay
- Emergency pause is the only risk limiter

## Trade-offs

**Pros:**
- Contains damage from a compromised or misconfigured peer route
- Keeps bridge limits reviewable at route granularity
- Allows different limits for hot, cold, or newly added routes

**Cons:**
- Adds configuration and monitoring per peer pair
- Legitimate bursts may be delayed by route-specific caps
- Limit changes need checkpointing to avoid refill surprises

## How It Works

Maintain independent buckets for each peer pair and direction. Before a send or receive completes, refill the bucket from elapsed time, then consume the requested amount.

```solidity
function _consumeOutbound(uint32 dstEid, uint256 amount) internal {
    Bucket storage b = outboundLimit[dstEid];
    _refill(b);
    require(b.available >= amount, "rate limited");
    b.available -= amount;
}

function _consumeInbound(uint32 srcEid, uint256 amount) internal {
    Bucket storage b = inboundLimit[srcEid];
    _refill(b);
    require(b.available >= amount, "rate limited");
    b.available -= amount;
}
```

When governance changes a route limit, checkpoint the old bucket first so accumulated capacity cannot be recalculated under the new cap unexpectedly.

## Implementation

### Key Points

- Key buckets by authenticated peer or endpoint, not only by token.
- Track inbound and outbound limits separately.
- Refill linearly from a stored checkpoint and cap at route capacity.
- Checkpoint before limit, window, or peer changes.
- Emit per-route limit updates and consumption failures for monitoring.
- Document that rate limiting may delay exits and define emergency bypass rules carefully.
- Per-token epoch caps are a weaker but useful companion when the bridge cannot key limits by route; do not describe them as peer isolation.

## Source Evidence

- EtherFi's weETH cross-chain contracts define per-peer inbound and outbound buckets in [`contracts/PairwiseRateLimiter.sol`](https://github.com/etherfi-protocol/weETH-cross-chain/blob/cc6c220847217df8f9dcc4ba19c1c349106a002c/contracts/PairwiseRateLimiter.sol).
- `EtherfiOFTUpgradeable.sol` integrates the limiter with LayerZero OFT send/receive paths, and `test/OFTDeployment.t.sol` covers inbound and outbound limits.
- Celer SGN volume control enforces per-token epoch caps before bridge relay and withdrawal payout in [`contracts/safeguard/VolumeControl.sol`](https://github.com/celer-network/sgn-v2-contracts/blob/b8a27161e0b700e30f30452c73418b60d133163f/contracts/safeguard/VolumeControl.sol), `contracts/liquidity-bridge/Bridge.sol`, and `contracts/liquidity-bridge/Pool.sol`; this is burst containment, not route-specific isolation.

## Real-World Examples

- EtherFi weETH cross-chain uses pairwise route buckets around OFT bridge flow.

## Related Patterns

- [Canonical Bridge Counterpart Validation](./pattern-canonical-bridge-counterpart-validation.md)
- [Version-Gated Message Endpoint Registry](./pattern-version-gated-message-endpoint-registry.md)
- [Threshold-Delayed Bridge Payout](./pattern-threshold-delayed-bridge-payout.md)
- [Bridge Exit Liveness Requirements](./req-bridge-exit-liveness.md)

## References

- See Source Evidence.
