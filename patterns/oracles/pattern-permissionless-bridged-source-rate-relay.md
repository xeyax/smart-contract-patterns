# Permissionless Bridged Source Rate Relay

> Let anyone relay a deterministic source-chain exchange rate through an authenticated bridge while keeping freshness and deviation checks explicit.

## Metadata

| Property | Value |
|----------|-------|
| Category | oracles |
| Tags | oracle, bridge, exchange-rate, permissionless-relay, source-chain |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A destination chain needs a source-chain staking or vault exchange rate
- The source contract exposes a deterministic rate and timestamp
- Bridge authentication already proves the remote sender
- Relay permissionlessness is preferred over trusted reporters

## Avoid When

- The source rate is manipulable in the same transaction as relay submission
- The bridge cannot authenticate source contract and chain
- Consumers cannot tolerate bridge delays or stale source data
- A reporter quorum is required for subjective valuation

## How It Works

Any caller submits a source-chain message through the canonical bridge path. The destination oracle accepts only messages from the configured source contract and records the relayed rate plus the source update time:

```solidity
function receiveRate(uint256 rate, uint256 sourceUpdatedAt) external onlyBridgePeer {
    require(sourceUpdatedAt > lastSourceUpdatedAt, "old source");
    require(block.timestamp - sourceUpdatedAt <= maxSourceAge, "stale source");
    require(_withinDeviation(rate, lastRate, maxDeltaBps), "rate jump");

    lastRate = rate;
    lastSourceUpdatedAt = sourceUpdatedAt;
    lastRelayAt = block.timestamp;
}
```

The relay caller is untrusted. Safety comes from source-chain determinism, bridge peer authentication, source timestamp propagation, and consumer-side bounds.

## Key Points

- Separate source freshness from destination relay execution time.
- Reject non-monotonic source timestamps and excessive rate jumps.
- Reject reports whose source timestamp is too old even when the destination relay transaction is fresh.
- Keep bridge peer replacement behind high-scrutiny governance.
- Document whether consumers should fail closed when relay updates stop.
- Do not present permissionless relay as reporter consensus.
- If the destination contract accepts only an authorized source sender, still require consumer-side max age and deviation checks; source authentication alone does not bound relay delay.

## Source Evidence

- Rocket Pool's Polygon oracle lets any caller submit the source-chain rate through the authenticated root/child tunnel and exposes the bridged value through a Balancer-style rate provider.
- Pendle's cross-chain exchange-rate app is a contrasting trusted-sender design: it accepts newer source timestamps but lacks max source-age and deviation bounds, so treat it as risk evidence rather than a permissionless relay exemplar.
- Kelp `CrossChainRateReceiver` authenticates LayerZero endpoint, source chain id, and source rate-provider address before applying relayed rate data, while `CrossChainRateProvider` and `MultiChainRateProvider` expose permissionless `updateRate` relays in `/private/tmp/defillama-source/Kelp-DAO__LRT-rsETH/contracts/cross-chain`.

## Related Patterns

- [Authenticated Root-Child Tunnel](../cross-chain/pattern-authenticated-root-child-tunnel.md)
- [Historical Bounds](./pattern-historical-bounds.md)
- [Oracle Staleness Risk](./risk-oracle-staleness.md)
