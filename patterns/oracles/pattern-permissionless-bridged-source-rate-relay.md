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

## Trade-offs

**Pros:**
- No trusted reporter set: any caller can relay, so no single operator's liveness or honesty gates updates.
- Bridge peer authentication plus source-chain determinism leave relayers unable to forge rates.
- Propagating the source timestamp lets consumers bound real data age, not just relay execution time.
- Monotonicity and deviation checks limit damage from delayed, reordered, or replayed messages.

**Cons:**
- Inherits the bridge's entire trust and failure model; a bridge compromise is an oracle compromise.
- Bridge latency makes the rate stale by construction, ruling out consumers that need tight freshness.
- Liveness still depends on someone paying to relay; updates can quietly stop, so consumers need explicit fail-closed policy.
- Deviation bounds are delicate to tune: too tight bricks legitimate rate moves, too loose admits large stale jumps.
- The account-slice variant adds a wide verification checklist (account, owner, commitment, slot, epoch) that is easy to under-check.

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

### Account-Slice Query Variant

For source chains where a bridge can attest arbitrary account data, the relay can
authenticate a fixed account, owner program, commitment level, and byte slice
instead of a remote app sender:

```solidity
function updateRate(bytes calldata response) external {
    Query memory q = _verifyBridgeQuery(response);
    require(q.chainId == SOURCE_CHAIN, "wrong chain");
    require(q.account == STAKE_POOL_ACCOUNT, "wrong account");
    require(q.owner == STAKE_POOL_PROGRAM, "wrong owner");
    require(q.commitment == FINALIZED, "weak commitment");
    require(q.slot > lastSlot, "old slot");
    require(block.timestamp - q.sourceTimestamp <= maxSourceAge, "stale");
    require(_clockEpoch(q) == _stakePoolEpoch(q), "epoch mismatch");

    _storeRate(_decodeRate(q.data), q.slot, q.sourceTimestamp);
}
```

This keeps the updater permissionless while making the bridge proof commit to
the exact source account fragment used for the rate.

## Key Points

- Separate source freshness from destination relay execution time.
- Reject non-monotonic source timestamps and excessive rate jumps.
- Reject reports whose source timestamp is too old even when the destination relay transaction is fresh.
- Keep bridge peer replacement behind high-scrutiny governance.
- Document whether consumers should fail closed when relay updates stop.
- Do not present permissionless relay as reporter consensus.
- If the destination contract accepts only an authorized source sender, still require consumer-side max age and deviation checks; source authentication alone does not bound relay delay.
- For account-data proofs, authenticate the account address, owner program, requested slice, commitment level, monotonic slot, source timestamp, and any source-chain epoch fields used by the rate.

## Source Evidence

- Rocket Pool's Polygon oracle lets any caller submit the source-chain rate through the authenticated root/child tunnel and exposes the bridged value through a Balancer-style rate provider.
- Pendle's cross-chain exchange-rate app is a contrasting trusted-sender design: it accepts newer source timestamps but lacks max source-age and deviation bounds, so treat it as risk evidence rather than a permissionless relay exemplar.
- Kelp `CrossChainRateReceiver` authenticates LayerZero endpoint, source chain id, and source rate-provider address before applying relayed rate data, while `CrossChainRateProvider` and `MultiChainRateProvider` expose permissionless `updateRate` relays in [`contracts/cross-chain`](https://github.com/Kelp-DAO/LRT-rsETH/blob/3dded885f6f797f5959aff449c3a30c5cbb6ce23/contracts/cross-chain).
- JitoSOL's Wormhole updater accepts permissionless query responses only for the configured Solana stake-pool account, owner, finalized commitment, monotonic slot, fresh source time, and matching stake-pool and clock epochs in [`src/StakePoolRate.sol`](https://github.com/jito-foundation/jitosol-wormhole-updater/blob/f5992a9c899072643613b1f2e3a53c02c2e0aadc/src/StakePoolRate.sol).

## Related Patterns

- [Authenticated Root-Child Tunnel](../cross-chain/pattern-authenticated-root-child-tunnel.md)
- [Historical Bounds](./pattern-historical-bounds.md)
- [Oracle Staleness Risk](./risk-oracle-staleness.md)
- [Stake Pool Epoch Accounting Freshness](../vaults/req-stake-pool-epoch-accounting-freshness.md)
