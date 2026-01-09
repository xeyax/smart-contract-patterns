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

## Real-World Incidents

- **Venus Protocol (2021)** — stale price for XVS allowed borrowing at wrong rate
- **Compound (2020)** — DAI oracle manipulation during flash crash
- **Arbitrum Sequencer Outage** — multiple protocols affected by stale prices

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

