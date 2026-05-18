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

### Rate-Limited Accepted State

For stateful oracle reports, validate both cadence and magnitude before mutating the accepted value:

```solidity
function acceptReport(uint256 newValue, uint256 reportTime) external {
    require(reportTime > lastReportTime, "non-monotonic");
    require(block.timestamp - reportTime <= maxReportAge, "stale");
    require(reportTime <= block.timestamp + maxFutureDrift, "future report");
    require(block.timestamp >= lastAcceptedAt + minUpdateInterval, "too soon");
    require(_withinDeviation(newValue, lastAcceptedValue, maxDeltaBps), "too far");

    lastAcceptedValue = newValue;
    lastAcceptedAt = block.timestamp;
    lastReportTime = reportTime;
}
```

This variant is useful for reporter-quorum systems and cross-chain price relays where each accepted update becomes protocol state. Reject zero values, undercollateralized rates, non-monotonic timestamps, excessive deltas, stale reports, and future-dated reports before minting, borrowing, or accepting deposits against the value.

### Anchor-Capped Accepted State

For reporter-fed prices, cap updates against an anchor over a fixed period:

```solidity
function validateReporterUpdate(uint256 reporterPrice, uint256 anchorPrice) internal view {
    uint256 deviation = _deviationBps(reporterPrice, anchorPrice);
    require(deviation <= maxSwingBps, "anchor deviation");
    require(block.number >= lastAnchorBlock + anchorPeriod, "anchor period active");
}
```

This reduces the chance that a reporter can move accepted state too far from a reference source in one update window. The anchor can be a TWAP, median, or prior accepted state, but it must have its own freshness and manipulation-resistance checks.

### External-Anchor Accepted State

For RWA or NAV-style feeds, accepted-state updates can require both a fresh external reference and a bounded move from the previous accepted value:

```solidity
function acceptNav(uint256 newNav, uint256 externalPrice, uint256 externalUpdatedAt) external {
    require(externalPrice > 0, "bad anchor");
    require(block.timestamp - externalUpdatedAt <= maxAnchorAge, "stale anchor");
    require(block.timestamp >= lastAcceptedAt + minCadence, "too soon");
    require(_withinAbsBound(newNav, externalPrice, maxAnchorDeltaBps), "anchor delta");
    require(_withinDelta(newNav, lastAcceptedValue, maxStateDeltaBps), "state delta");

    lastAcceptedValue = newNav;
    lastAcceptedAt = block.timestamp;
}
```

This constrains accepted-state movement; it is not a freshness guarantee by itself. The external anchor must still have round freshness, nonzero values, and monotonic update checks.

### One-Sided Stablecoin Cap

For assets intended not to exceed a peg, a one-sided cap can preserve downside depeg while preventing upward overvaluation:

```solidity
function cappedPrice() external view returns (uint256) {
    uint256 price = source.price();
    return price > maxPegPrice ? maxPegPrice : price;
}
```

This is safer than forcing the price to a constant peg because it does not hide downside moves. It should be used only when upward premium should not increase borrowing power, mint value, or collateral value.

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
- Bound both value movement and update cadence for accepted-state oracles
- Accepted-state bounds constrain mutations, but do not prove source liveness unless the anchor or reporter timestamp is also fresh
- For bridged prices, authenticate the remote sender and reject stale, future-dated, or non-monotonic timestamps
- For stable or pegged collateral, prefer one-sided caps that limit upward overvaluation without masking downside depeg
- Do not treat out-of-gas, empty-return, or unexpected-revert fallback paths as valid default prices

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
- SparkLend Advanced uses one-sided capped stablecoin-style oracle logic so upward overvaluation is limited without hiding downside depeg.
- An Ondo audit-contest snapshot combines fresh Chainlink round checks, daily cadence, absolute bounds, and anchor-delta bounds before accepting RWA oracle state.

## Related Patterns

- [Multi-Source Validation](./pattern-multi-source-validation.md) — combine bounds with source validation
- [Chainlink Integration](./pattern-chainlink-integration.md) — primary oracle to validate
- [TWAP Oracle](./pattern-twap-oracle.md) — reference for bounds
- [Peg Ratio Monitor](./pattern-peg-ratio-monitor.md) — monitor market/fair-value divergence

## References

- [MakerDAO Oracle Security Module](https://docs.makerdao.com/smart-contract-modules/oracle-module)
- [Price Oracle Best Practices](https://blog.openzeppelin.com/secure-oracle-design)
