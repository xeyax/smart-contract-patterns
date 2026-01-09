# Historical Bounds

> Validate price against historical min/max to detect anomalies and extreme deviations.

## Metadata

| Property | Value |
|----------|-------|
| Category | oracles |
| Tags | oracle, bounds, validation, anomaly-detection, sanity-check |
| Complexity | Low |
| Gas Efficiency | Medium |
| Audit Risk | Low |

## Use When

- Need sanity check for oracle prices
- Want to detect extreme price movements
- Building circuit breaker or safety mechanism
- As additional validation layer

## Avoid When

- Asset is expected to have large price swings
- Historical data is not available
- Need to handle legitimate flash crashes
- Storage cost is critical

## Trade-offs

**Pros:**
- Simple implementation
- Catches extreme anomalies
- Low computation cost
- Works with any price source

**Cons:**
- Doesn't detect slow drift
- Requires historical data maintenance
- May reject legitimate price moves
- Bounds need periodic updates

## How It Works

Track price history and reject values outside acceptable range:

```
if price < minBound || price > maxBound:
    revert("Price outside historical bounds")
```

Bounds can be:
- **Fixed:** Set by governance
- **Rolling:** Min/max over recent period
- **Percentile-based:** 5th/95th percentile of history

## Requirements Satisfied

This pattern satisfies [Oracle Reliability Requirements](./req-oracle-reliability.md):
- **R2: Accuracy** — rejects obviously wrong prices
- Useful as supplementary validation, not primary oracle

## Implementation

### Fixed Bounds

```solidity
contract FixedBoundsOracle {
    uint256 public minPrice;
    uint256 public maxPrice;

    function validatePrice(uint256 price) public view returns (bool) {
        return price >= minPrice && price <= maxPrice;
    }

    function getPriceWithValidation() external view returns (uint256) {
        uint256 price = _getOraclePrice();
        require(validatePrice(price), "Price outside bounds");
        return price;
    }

    // Governance can update bounds
    function setBounds(uint256 _min, uint256 _max) external onlyGovernance {
        require(_min < _max, "Invalid bounds");
        minPrice = _min;
        maxPrice = _max;
    }

    function _getOraclePrice() internal view returns (uint256);
}
```

### Rolling Min/Max

```solidity
contract RollingBoundsOracle {
    uint256 public constant HISTORY_SIZE = 24;  // e.g., 24 hourly observations
    uint256 public constant BOUND_MARGIN_BPS = 2000;  // 20% outside min/max

    uint256[24] public priceHistory;
    uint256 public historyIndex;
    uint256 public lastUpdateTime;
    uint256 public updateInterval = 1 hours;

    function recordPrice() external {
        require(block.timestamp >= lastUpdateTime + updateInterval, "Too soon");

        uint256 currentPrice = _getOraclePrice();
        priceHistory[historyIndex] = currentPrice;
        historyIndex = (historyIndex + 1) % HISTORY_SIZE;
        lastUpdateTime = block.timestamp;
    }

    function getBounds() public view returns (uint256 minBound, uint256 maxBound) {
        uint256 minPrice = type(uint256).max;
        uint256 maxPrice = 0;

        for (uint i = 0; i < HISTORY_SIZE; i++) {
            if (priceHistory[i] == 0) continue;  // Skip uninitialized
            if (priceHistory[i] < minPrice) minPrice = priceHistory[i];
            if (priceHistory[i] > maxPrice) maxPrice = priceHistory[i];
        }

        // Add margin
        minBound = minPrice * (10000 - BOUND_MARGIN_BPS) / 10000;
        maxBound = maxPrice * (10000 + BOUND_MARGIN_BPS) / 10000;
    }

    function validatePrice(uint256 price) public view returns (bool) {
        (uint256 minBound, uint256 maxBound) = getBounds();
        return price >= minBound && price <= maxBound;
    }
}
```

### Percentage-Based Bounds

```solidity
contract PercentageBoundsOracle {
    uint256 public lastKnownGoodPrice;
    uint256 public maxDeviationBps = 5000;  // 50% max deviation

    function validateAndUpdate(uint256 newPrice) public returns (bool valid) {
        if (lastKnownGoodPrice == 0) {
            // First price, accept it
            lastKnownGoodPrice = newPrice;
            return true;
        }

        uint256 deviation = _calculateDeviation(newPrice, lastKnownGoodPrice);

        if (deviation <= maxDeviationBps) {
            lastKnownGoodPrice = newPrice;
            return true;
        }

        return false;  // Reject extreme deviation
    }

    function _calculateDeviation(uint256 a, uint256 b) internal pure returns (uint256) {
        uint256 diff = a > b ? a - b : b - a;
        return diff * 10000 / b;
    }
}
```

### With Rate Limiting

Prevent rapid extreme changes:

```solidity
contract RateLimitedBoundsOracle {
    uint256 public lastPrice;
    uint256 public lastPriceTime;
    uint256 public maxChangePerHourBps = 1000;  // 10% per hour max

    function validatePriceChange(uint256 newPrice) public view returns (bool) {
        if (lastPrice == 0) return true;

        uint256 timeDelta = block.timestamp - lastPriceTime;
        uint256 maxAllowedChange = lastPrice * maxChangePerHourBps * timeDelta / (10000 * 1 hours);

        uint256 actualChange = newPrice > lastPrice ?
            newPrice - lastPrice :
            lastPrice - newPrice;

        return actualChange <= maxAllowedChange;
    }
}
```

## Calibration

| Asset Type | Suggested Max Deviation | Rationale |
|------------|-------------------------|-----------|
| Stablecoins | 5% | Should be very stable |
| ETH, BTC | 30-50% | Can have significant moves |
| Altcoins | 50-100% | High volatility expected |

**Considerations:**
- Too tight: rejects legitimate price moves
- Too loose: doesn't catch anomalies
- Consider asset-specific volatility patterns

## Limitations

### Doesn't Detect Slow Drift

If price drifts slowly over time, bounds will update to accommodate:

```
Day 1: Price = $100, Bounds = [$80, $120]
Day 2: Price = $110, Bounds = [$88, $132]  (adjusted)
Day 3: Price = $120, Bounds = [$96, $144]  (adjusted)
...
Day N: Attacker has slowly moved price 50% without triggering bounds
```

**Mitigation:** Combine with absolute bounds or longer historical window.

### Flash Crash Handling

Legitimate flash crashes may be rejected:

```
Normal price: $100
Flash crash: $50 (legitimate market event)
Bounds: [$80, $120]
Result: Legitimate price rejected!
```

**Mitigation:** Use time-delayed validation or allow governance override.

## Integration with Circuit Breaker

```solidity
contract CircuitBreakerWithBounds {
    HistoricalBoundsOracle public boundsOracle;
    bool public circuitBreakerTriggered;

    modifier boundsCheck() {
        uint256 price = _getOraclePrice();

        if (!boundsOracle.validatePrice(price)) {
            circuitBreakerTriggered = true;
            emit CircuitBreakerTriggered(price);
            revert("Price outside historical bounds");
        }

        _;
    }

    function deposit(uint256 amount) external boundsCheck {
        // ... deposit logic
    }
}
```

## Real-World Examples

- [MakerDAO OSM](https://docs.makerdao.com/smart-contract-modules/oracle-module/oracle-security-module-osm-detailed-documentation) — price bounds with delay
- [Chainlink Circuit Breakers](https://blog.chain.link/circuit-breakers-and-client-diversity-within-the-chainlink-network/) — built-in bounds checking

## Related Patterns

- [Multi-Source Validation](./pattern-multi-source-validation.md) — combine bounds with source validation
- [Chainlink Integration](./pattern-chainlink-integration.md) — primary oracle to validate
- [TWAP Oracle](./pattern-twap-oracle.md) — reference for bounds

## References

- [MakerDAO Oracle Security Module](https://docs.makerdao.com/smart-contract-modules/oracle-module)
- [Price Oracle Best Practices](https://blog.openzeppelin.com/secure-oracle-design)

