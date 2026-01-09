# Chainlink Integration

> Integrate Chainlink price feeds for reliable off-chain oracle data with built-in manipulation resistance.

## Metadata

| Property | Value |
|----------|-------|
| Category | oracles |
| Tags | oracle, chainlink, off-chain, price-feed |
| Complexity | Low |
| Gas Efficiency | High |
| Audit Risk | Low |

## Use When

- Need manipulation-resistant price for major assets
- Asset has Chainlink feed available
- Trust Chainlink's decentralized oracle network
- Want simple, battle-tested integration

## Avoid When

- Asset has no Chainlink feed
- Need price for long-tail/new tokens
- Require real-time price (Chainlink has latency)
- Zero external dependencies required

## Trade-offs

**Pros:**
- Battle-tested, widely used
- Resistant to on-chain manipulation
- Simple integration
- High coverage for major assets

**Cons:**
- Centralization risk (trust Chainlink nodes)
- Can be stale (deviation threshold delays updates)
- Not available for all assets
- External dependency

## How It Works

Chainlink aggregates prices from multiple independent node operators:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Node 1    │    │   Node 2    │    │   Node N    │
│  (Exchange  │    │  (Exchange  │    │  (Exchange  │
│   data)     │    │   data)     │    │   data)     │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
       └────────────┬─────┴──────────────────┘
                    │
              ┌─────▼─────┐
              │ Aggregator│ ─── Median/consensus
              └─────┬─────┘
                    │
              ┌─────▼─────┐
              │  On-chain │ ─── latestRoundData()
              │   Feed    │
              └───────────┘
```

Updates occur when:
- Price deviates beyond threshold (e.g., 0.5% for ETH/USD)
- Heartbeat timeout (e.g., 1 hour)

## Requirements Satisfied

This pattern satisfies [Oracle Reliability Requirements](./req-oracle-reliability.md):
- **R1: Freshness** — heartbeat ensures periodic updates
- ⚠️ **R2: Accuracy** — deviation threshold means price can be off by up to threshold %
- **R3: Manipulation Resistance** — off-chain aggregation defeats on-chain attacks
- ⚠️ **R4: Availability** — dependent on Chainlink infrastructure

## Implementation

### Basic Integration

```solidity
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract ChainlinkOracle {
    AggregatorV3Interface public immutable priceFeed;
    uint256 public maxStaleness;  // e.g., 3600 = 1 hour

    constructor(address _priceFeed, uint256 _maxStaleness) {
        priceFeed = AggregatorV3Interface(_priceFeed);
        maxStaleness = _maxStaleness;
    }

    function getPrice() public view returns (uint256) {
        (
            uint80 roundId,
            int256 price,
            uint256 startedAt,
            uint256 updatedAt,
            uint80 answeredInRound
        ) = priceFeed.latestRoundData();

        // Validate freshness
        require(updatedAt >= block.timestamp - maxStaleness, "Stale price");

        // Validate round completeness
        require(answeredInRound >= roundId, "Round not complete");

        // Validate positive price
        require(price > 0, "Invalid price");

        return uint256(price);
    }

    function getDecimals() public view returns (uint8) {
        return priceFeed.decimals();
    }
}
```

**Note:** Chainlink USD pairs typically use 8 decimals. Normalize prices before use.

### With Fallback Oracle

```solidity
contract ChainlinkWithFallback {
    AggregatorV3Interface public primaryFeed;
    AggregatorV3Interface public fallbackFeed;
    uint256 public maxStaleness;

    function getPrice() public view returns (uint256) {
        // Try primary first
        try this.getPriceFromFeed(primaryFeed) returns (uint256 price) {
            return price;
        } catch {
            // Fallback to secondary
            return getPriceFromFeed(fallbackFeed);
        }
    }

    function getPriceFromFeed(AggregatorV3Interface feed) public view returns (uint256) {
        (, int256 price, , uint256 updatedAt, ) = feed.latestRoundData();
        require(updatedAt >= block.timestamp - maxStaleness, "Stale");
        require(price > 0, "Invalid");
        return uint256(price);
    }
}
```

### L2 Sequencer Check

On L2s (Arbitrum, Optimism), check sequencer uptime:

```solidity
contract L2ChainlinkOracle {
    AggregatorV3Interface public priceFeed;
    AggregatorV3Interface public sequencerUptimeFeed;
    uint256 public gracePeriod = 3600;  // 1 hour after sequencer comes back

    function getPrice() public view returns (uint256) {
        // Check sequencer status
        (, int256 answer, uint256 startedAt, , ) = sequencerUptimeFeed.latestRoundData();

        bool isSequencerUp = answer == 0;
        require(isSequencerUp, "Sequencer down");

        // Ensure grace period has passed since sequencer came back up
        uint256 timeSinceUp = block.timestamp - startedAt;
        require(timeSinceUp > gracePeriod, "Grace period not passed");

        // Now safe to read price
        return _getPriceFromFeed();
    }
}
```

## Staleness Configuration

| Asset Type | Heartbeat | Deviation | Suggested maxStaleness |
|------------|-----------|-----------|------------------------|
| ETH/USD | 1 hour | 0.5% | 3600 (1 hour) |
| BTC/USD | 1 hour | 0.5% | 3600 (1 hour) |
| Stablecoins | 24 hours | 0.25% | 86400 (24 hours) |
| Altcoins | 24 hours | 1% | 86400 (24 hours) |

**Important:** Check the actual feed parameters on [Chainlink Data Feeds](https://docs.chain.link/data-feeds/price-feeds/addresses).

## Common Pitfalls

| Pitfall | Check | Solution |
|---------|-------|----------|
| **No staleness check** | `updatedAt` | `require(block.timestamp - updatedAt <= maxStaleness)` |
| **Incomplete round** | `answeredInRound` | `require(answeredInRound >= roundId)` |
| **L2 sequencer down** | Sequencer feed | Check `answer == 0` and grace period on L2s |
| **Wrong decimals** | `decimals()` | Normalize to 18 decimals (most USD pairs use 8) |
| **Negative price** | `price` | `require(price > 0)` |

## Real-World Examples

- [Aave](https://docs.aave.com/developers/core-contracts/aaveoracle) — Chainlink for all price feeds
- [Compound](https://docs.compound.finance/v2/prices/) — Chainlink with fallbacks
- [MakerDAO](https://docs.makerdao.com/smart-contract-modules/oracle-module) — Chainlink + median

## Related Patterns

- [Multi-Source Validation](./pattern-multi-source-validation.md) — combine Chainlink with on-chain sources
- [TWAP Oracle](./pattern-twap-oracle.md) — on-chain alternative
- [Historical Bounds](./pattern-historical-bounds.md) — validate Chainlink against history

## References

- [Chainlink Data Feeds Documentation](https://docs.chain.link/data-feeds)
- [Chainlink Feed Addresses](https://docs.chain.link/data-feeds/price-feeds/addresses)
- [Chainlink L2 Sequencer Feeds](https://docs.chain.link/data-feeds/l2-sequencer-feeds)
- [Using Data Feeds Safely](https://docs.chain.link/data-feeds/using-data-feeds)

