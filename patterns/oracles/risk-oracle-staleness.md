# Oracle Staleness Risk

> Using outdated price data leads to incorrect valuations and creates arbitrage opportunities.

## Metadata

| Property | Value |
|----------|-------|
| Category | oracles |
| Tags | oracle, staleness, stale-price, risk |
| Type | Risk Description |

## Problem Description

Oracle prices become stale when the data source hasn't been updated recently. This creates a gap between the oracle price and the actual market price, enabling:
- Arbitrage at the expense of the protocol
- Incorrect liquidations (too early or too late)
- Unfair pricing for deposits/withdrawals

## Applies When

- Price or rate data has a heartbeat, deviation threshold, relay delay, or manual update cadence
- Contracts accept Chainlink-compatible wrappers, bridged rates, or internal exchange-rate feeds
- Value-bearing actions do not reject stale or synthetic timestamps
- Oracle downtime can affect deposits, withdrawals, borrowing, liquidation, or voting power

## Requirements Violated

This risk violates [Oracle Reliability Requirements](./req-oracle-reliability.md):
- **R1: Freshness** — price data is outdated

## Attack Vectors

### 1. Deposit During Stale Low Price

```
Chainlink ETH/USD: $1800 (stale, last update 2 hours ago)
Actual market: $2000

Vault NAV uses stale $1800
User deposits $1000, gets shares based on understated NAV
When price updates, user's shares are worth more than deposited

Profit: ($2000 - $1800) / $1800 × $1000 = $111
```

### 2. Withdraw During Stale High Price

```
Chainlink ETH/USD: $2200 (stale, last update 3 hours ago)
Actual market: $2000

User withdraws based on overstated $2200 NAV
Receives more assets than fair share

Profit: ($2200 - $2000) / $2000 × withdrawal_amount
```

### 3. Delayed Liquidation

```
Lending protocol uses stale price
Actual collateral value dropped below liquidation threshold
But stale oracle still shows safe

Result: Bad debt accumulates until oracle updates
```

### 4. Premature Liquidation

```
Flash crash causes DEX price to drop
Chainlink hasn't updated yet (within deviation threshold)
User's position is actually safe at current oracle price

If protocol uses faster oracle that DID update:
User gets liquidated at temporary bad price
```

## Why Staleness Occurs

### Chainlink Deviation Threshold

Chainlink only updates when:
- Price moves beyond deviation threshold (e.g., 0.5% for ETH/USD)
- Heartbeat timeout expires (e.g., 1 hour)

```
If price oscillates within 0.5%:
No update for up to 1 hour
During that hour, actual price might drift significantly
```

### Network Congestion

During high gas prices:
- Oracle updates may be delayed
- Staleness window extends
- Attackers exploit the gap

### L2 Sequencer Downtime

On L2s (Arbitrum, Optimism):
- Sequencer goes offline
- No transactions processed, including oracle updates
- When sequencer restarts, prices are stale
- Lending protocols may need action-level sentinels that block borrows and liquidations during the downtime and post-restart grace period.

### Chainlink-Compatible Shims

Some contracts expose a Chainlink-like interface while deriving the answer from a staking exchange rate, DEX TWAP, bridged price, or internal conversion. If the shim returns `updatedAt = block.timestamp`, a generic staleness check passes even when the underlying source has no freshness guarantee.

Treat wrappers as new oracle implementations:

- Inspect how the answer is computed.
- Propagate the oldest underlying timestamp through `updatedAt`.
- Reject `latestAnswer()` integrations for value-bearing operations because they cannot check freshness.
- Do not rely on off-chain monitoring as the only guard for on-chain state changes.
- For bridged rate providers, distinguish source update time from destination relay time; `block.timestamp` on the destination proves only when the message executed.
- A fallback oracle that triggers only when a source is missing or non-positive is not multi-source validation if it ignores source freshness.

### Conservative Zeroing Can Still Be Liveness Risk

Some voting-power or validator-set calculators fail closed by returning zero when a price is stale or unavailable. This is safer than overvaluing assets for solvency, but it can still distort quorum, validator-set fairness, or chain representation if one component unexpectedly drops to zero.

### Stale-To-Peg Fallback

Stable-asset adapters sometimes return par value when an upstream price is stale
or unavailable. That can preserve liveness for low-risk views, but it is
fail-open for mint, redeem, borrow, and allocation paths because it masks both
oracle outages and real depegs.

### Stale Price Degradation Without Clear Action Scope

Some systems degrade stale or broken price ranges toward conservative extremes
instead of reverting immediately. This can be useful when the degraded range
forces conservative accounting, but it must be paired with action-specific rules
that say which actions can continue under degraded prices and which must stop.

### Emergency Containment Blocked By Stale Reads

Fail-closed stale-price checks are appropriate for value-bearing user actions, but they can be counterproductive on pure risk-reduction setters. If lowering a borrow cap, LTV, mint limit, or route limit does not need the current price, requiring a fresh oracle read can block containment during the exact outage the limiter is meant to handle.

## Conditions That Increase Risk

| Factor | Higher Risk | Lower Risk |
|--------|-------------|------------|
| Update frequency | Low (hourly) | High (every block) |
| Deviation threshold | High (1-2%) | Low (0.1%) |
| Market volatility | High | Low |
| Heartbeat interval | Long (24 hours) | Short (1 hour) |
| Network congestion | High | Low |

## Impact Calculation

Potential profit from staleness:

```
max_profit = operation_size × deviation_threshold

Example (1% deviation threshold):
- $10M deposit → up to $100K arbitrage
- Profit extracted from other users/protocol
```

## Mitigations

| Pattern | How It Helps | Trade-off |
|---------|--------------|-----------|
| [Multi-Source Validation](./pattern-multi-source-validation.md) | Detects when oracle differs from TWAP/spot | Higher gas cost |
| [TWAP Oracle](./pattern-twap-oracle.md) | On-chain source updates every block | Lags during volatility |
| Staleness Check | Reject stale prices | May block operations |
| Premium Buffer | Fee covers potential staleness | Cost to users |
| Source Timestamp Propagation | Prevents wrappers from hiding stale inputs | Requires wrapper-specific integration |
| L2 Action Sentinel | Blocks borrow/liquidation paths during sequencer downtime or grace period | Can delay liquidations unless a severe-risk exception exists |
| Conservative Zeroing | Avoids overvaluing stale-priced components | Can change quorum or validator-set composition abruptly |
| Reject Stale-To-Peg Fallbacks | Prevents stable-asset adapters from silently blessing outages at par | May block actions during benign oracle downtime |
| Risk-Reduction Setter Exemption | Lets emergency actions lower exposure during oracle outages | Must be limited to monotonic reductions that do not depend on price |
| Stale Price Degradation | Keeps conservative views available during feed failure | Must not be used as a generic fresh price for all actions |

### Implementation: Staleness Check

```solidity
function getChainlinkPrice() internal view returns (uint256) {
    (, int256 price, , uint256 updatedAt, ) = priceFeed.latestRoundData();

    // Check staleness
    require(
        block.timestamp - updatedAt <= MAX_STALENESS,
        "Price too stale"
    );

    require(price > 0, "Invalid price");
    return uint256(price);
}
```

### Implementation: L2 Sequencer Check

```solidity
function getL2Price() internal view returns (uint256) {
    // Check sequencer status first
    (, int256 answer, uint256 startedAt, , ) = sequencerFeed.latestRoundData();

    bool isSequencerUp = answer == 0;
    require(isSequencerUp, "Sequencer down");

    // Grace period after sequencer comes back
    require(
        block.timestamp - startedAt > GRACE_PERIOD,
        "Grace period active"
    );

    return getChainlinkPrice();
}
```

For lending, also gate the value-changing action:

```solidity
require(oracleSentinel.isBorrowAllowed(), "sequencer grace");
```

## Detection

### On-Chain Detection

```solidity
function isPriceStale() public view returns (bool) {
    (, , , uint256 updatedAt, ) = priceFeed.latestRoundData();
    return block.timestamp - updatedAt > maxStaleness;
}
```

### Off-Chain Monitoring

- Alert when `updatedAt` exceeds threshold
- Monitor deviation between Chainlink and DEX prices
- Track sequencer status on L2s
- For voting-power calculators, alert when stale or missing feeds zero a component that contributes to quorum.
- For emergency playbooks, test that stale or unavailable price feeds do not block monotonic risk reductions that do not use the price.
- For degraded price ranges, test which actions remain enabled and prove the degraded range is conservative for those actions.

## Real-World Incidents

- **Venus Protocol (2021)** — stale price for XVS allowed borrowing at wrong rate
- **Compound (2020)** — DAI oracle manipulation during flash crash
- **Arbitrum Sequencer Outage** — multiple protocols affected by stale prices
- Rocket Pool's Polygon rate relay and Symbiotic Relay's voting-power calculators show wrapper-specific freshness hazards: the former can confuse source and destination timestamps, while the latter can zero voting power on stale prices.
- Reserve Protocol collateral plugins cache price bounds and degrade stale or broken prices toward conservative low/high extremes while collateral default handling is delayed, as implemented under `/private/tmp/defillama-source/reserve-protocol__protocol/contracts/plugins/assets`.
- Aave V2's oracle integration illustrates the modern risk: `getAssetPrice` reads Chainlink-style `latestAnswer()` and falls back only for missing or non-positive answers, even though the interface exposes timestamps.
- Reservoir adapters return par-like values when Chainlink-style answers are stale and the PSM consumes `latestAnswer()` without a timestamp in `/private/tmp/defillama-source/reservoir-protocol__reservoir/src/adapters` and `src/PegStabilityModule.sol`.

## Related Patterns

- [Multi-Source Validation](./pattern-multi-source-validation.md) — cross-check detects staleness
- [Chainlink Integration](./pattern-chainlink-integration.md) — proper integration with staleness checks
- [TWAP Oracle](./pattern-twap-oracle.md) — alternative with different trade-offs

## Related Risks

- [Price Manipulation Risk](./risk-price-manipulation.md) — different vector, similar impact
- [Oracle Frontrunning Risk](./risk-oracle-frontrunning.md) — exploits predictable updates

## References

- [Chainlink Deviation and Heartbeat](https://docs.chain.link/data-feeds)
- [L2 Sequencer Uptime Feeds](https://docs.chain.link/data-feeds/l2-sequencer-feeds)
- [Oracle Security Best Practices](https://blog.openzeppelin.com/secure-oracle-design)
