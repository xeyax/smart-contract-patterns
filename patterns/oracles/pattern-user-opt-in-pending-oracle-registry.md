# User Opt-In Pending Oracle Registry

> Stage oracle replacements behind a delay while allowing selected users or vaults to opt into the pending oracle early.

## Metadata

| Property | Value |
|----------|-------|
| Category | oracles |
| Tags | oracle, registry, timelock, migration, opt-in |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Oracle migrations need a review delay before global activation
- Some vaults or users may need to migrate early to avoid stale or disabled feeds
- Consumers can tolerate intentional per-vault oracle divergence during the transition
- The registry can expose which oracle each consumer currently uses

## Avoid When

- The protocol requires one canonical price source for every user at all times
- Cross-user price divergence creates arbitrage or fairness problems
- Consumers cannot safely handle disabled current oracles
- There is no monitoring for pending, committed, and user-accepted feed state

## Trade-offs

**Pros:**
- Gives governance or operators a delay before global feed replacement
- Lets risk-aware consumers adopt the pending feed early
- Provides an explicit disabled-feed failure mode

**Cons:**
- Two users may legitimately see different oracle sources during the window
- Integrators must query effective oracle, not only current global oracle
- More state transitions and edge cases than a simple registry

## How It Works

The registry stores current and pending oracles per asset. Governance schedules a pending oracle with an activation time:

```solidity
function scheduleOracle(address asset, address next) external onlyOwner {
    pendingOracle[asset] = next;
    pendingOracleReadyAt[asset] = block.timestamp + delay;
}

function acceptPendingOracle(address asset) external {
    userOracleOverride[msg.sender][asset] = pendingOracle[asset];
}

function commitOracle(address asset) external {
    require(block.timestamp >= pendingOracleReadyAt[asset], "delay");
    currentOracle[asset] = pendingOracle[asset];
    pendingOracle[asset] = address(0);
}
```

If the current oracle is disabled, consumers must either use a valid accepted pending oracle or fail closed.

### Maturity-Gated Feed Switch Variant

For fixed-maturity instruments, the effective feed can switch automatically at maturity while pre-maturity replacement remains timelocked:

```solidity
function latestRoundData() external view returns (Round memory) {
    if (block.timestamp >= maturity) return afterMaturity.latestRoundData();
    if (block.timestamp >= switchReadyAt) return pendingFeed.latestRoundData();
    return previousFeed.latestRoundData();
}
```

This variant should expose whether a switch is queued, reject maturity-in-the-past deployment, and preserve feed decimals and freshness semantics across both feeds.

## Implementation

### Key Points
- Expose `effectiveOracle(user, asset)` so callers do not assume global uniformity.
- Emit events for schedule, commit, disable, and user opt-in.
- Prevent opt-in to stale, zero, or superseded pending oracles.
- Document whether opt-in is per-user, per-vault, or per-asset.
- Treat oracle divergence as a fairness and accounting risk in shared pools.
- Keep removal of an active underlying or oracle blocked until dependent consumers migrate.
- For maturity-gated switches, test pre-maturity queued state, cancellation, maturity override, and decimal mismatch rejection.

## Source Evidence

- Aera v3 schedules oracle updates, commits them after a delay, disables current oracles, and lets consumers accept a pending oracle before global commit in `/private/tmp/defillama-source/aera-finance__aera-contracts-public/v3/src/periphery/OracleRegistry.sol`.
- Inverse FiRM switches Pendle PT feeds through a timelock before maturity and automatically uses the after-maturity feed once maturity passes in `/private/tmp/defillama-source/InverseFinance__FiRM/src/util/FeedSwitch.sol`.

## Real-World Examples

- Aera v3 supports delayed oracle replacement with early opt-in for specific vault/user contexts.

## Related Patterns

- [Timelocked Address Registry](../upgrades/pattern-timelocked-address-registry.md)
- [Oracle Reliability Requirements](./req-oracle-reliability.md)
- [Exchange-Rate Valuation Risk](./risk-exchange-rate-valuation.md)
- [Historical Bounds](./pattern-historical-bounds.md)
