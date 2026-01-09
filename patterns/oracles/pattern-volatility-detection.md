# Volatility Detection

> Measure asset volatility by comparing spot, TWAP, and oracle prices to detect market stress, trigger circuit breakers, or adjust dynamic premiums.

## Metadata

| Property | Value |
|----------|-------|
| Category | oracles |
| Tags | oracle, volatility, deviation, risk, twap, spot, monitoring |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Low |

## Use When

- Vault needs to adjust fees based on market conditions
- Want to detect oracle staleness or manipulation
- Building circuit breaker logic
- Need risk scoring for multi-asset portfolios
- Implementing dynamic slippage protection

## Avoid When

- Single price source is sufficient for use case
- Gas costs of multiple oracle calls are prohibitive
- Asset has no reliable secondary price source
- Real-time (<1 block) volatility needed

## Trade-offs

**Pros:**
- Detects abnormal market conditions
- Identifies stale or manipulated oracles
- Enables adaptive risk management
- Works with any combination of price sources

**Cons:**
- Multiple oracle calls increase gas cost
- False positives during legitimate volatility
- Requires calibration per asset type
- TWAP inherently lags spot during rapid moves

## How It Works

### Price Source Comparison

```
┌────────────────────────────────────────────────────────────────┐
│                   Price Source Deviation                        │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│   SPOT ◄─────── d₁ ───────► TWAP                               │
│     │                         │                                 │
│     │                         │                                 │
│    d₂                        d₃                                 │
│     │                         │                                 │
│     ▼                         ▼                                 │
│              ORACLE                                             │
│                                                                 │
│   d₁ = |spot - twap| / twap      Spot vs TWAP deviation        │
│   d₂ = |spot - oracle| / oracle  Spot vs Oracle deviation      │
│   d₃ = |twap - oracle| / oracle  TWAP vs Oracle deviation      │
│                                                                 │
│   Volatility Score = max(d₁, d₂, d₃)  or  weighted average     │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### Interpretation Matrix

| Spot vs TWAP | Spot vs Oracle | TWAP vs Oracle | Diagnosis | Action |
|:---:|:---:|:---:|---|---|
| ✅ | ✅ | ✅ | Normal conditions | Allow operations |
| ❌ | ✅ | ❌ | TWAP lagging (rapid move) | Allow with caution |
| ❌ | ❌ | ✅ | Oracle stale | Use TWAP, flag warning |
| ✅ | ❌ | ❌ | Spot manipulation | Use Oracle/TWAP |
| ❌ | ❌ | ❌ | High volatility or attack | Pause / increase premium |

## Implementation

### Core Volatility Detector

```solidity
contract VolatilityDetector {
    uint256 constant BPS = 10000;
    uint256 constant PRECISION = 1e18;

    struct VolatilityReport {
        uint256 spotPrice;
        uint256 twapPrice;
        uint256 oraclePrice;
        uint256 spotTwapDeviationBps;
        uint256 spotOracleDeviationBps;
        uint256 twapOracleDeviationBps;
        uint256 maxDeviationBps;
        bool isVolatile;
    }

    uint256 public volatilityThresholdBps = 300; // 3%
    uint32 public twapPeriod = 30 minutes;

    /// @notice Get comprehensive volatility report for an asset
    function getVolatilityReport(
        address token,
        address quoteToken
    ) external view returns (VolatilityReport memory report) {
        report.spotPrice = _getSpotPrice(token, quoteToken);
        report.twapPrice = _getTwapPrice(token, quoteToken, twapPeriod);
        report.oraclePrice = _getOraclePrice(token, quoteToken);

        report.spotTwapDeviationBps = _calculateDeviation(
            report.spotPrice,
            report.twapPrice
        );
        report.spotOracleDeviationBps = _calculateDeviation(
            report.spotPrice,
            report.oraclePrice
        );
        report.twapOracleDeviationBps = _calculateDeviation(
            report.twapPrice,
            report.oraclePrice
        );

        report.maxDeviationBps = _max3(
            report.spotTwapDeviationBps,
            report.spotOracleDeviationBps,
            report.twapOracleDeviationBps
        );

        report.isVolatile = report.maxDeviationBps > volatilityThresholdBps;
    }

    /// @notice Simple volatility check (gas-optimized)
    function isVolatile(
        address token,
        address quoteToken
    ) external view returns (bool) {
        uint256 spot = _getSpotPrice(token, quoteToken);
        uint256 twap = _getTwapPrice(token, quoteToken, twapPeriod);

        uint256 deviation = _calculateDeviation(spot, twap);
        return deviation > volatilityThresholdBps;
    }

    function _calculateDeviation(
        uint256 a,
        uint256 b
    ) internal pure returns (uint256) {
        if (b == 0) return BPS; // Max deviation if reference is zero
        if (a > b) {
            return (a - b) * BPS / b;
        }
        return (b - a) * BPS / a;
    }

    function _max3(uint256 a, uint256 b, uint256 c) internal pure returns (uint256) {
        return a > b ? (a > c ? a : c) : (b > c ? b : c);
    }

    // Abstract price getters
    function _getSpotPrice(address token, address quote) internal view virtual returns (uint256);
    function _getTwapPrice(address token, address quote, uint32 period) internal view virtual returns (uint256);
    function _getOraclePrice(address token, address quote) internal view virtual returns (uint256);
}
```

### Historical Volatility Tracker

Track volatility over time for trend analysis:

```solidity
contract HistoricalVolatilityTracker {
    uint256 constant BPS = 10000;

    struct PriceObservation {
        uint256 price;
        uint32 timestamp;
    }

    // token => observations (circular buffer)
    mapping(address => PriceObservation[]) public priceHistory;
    mapping(address => uint256) public historyIndex;

    uint256 public maxHistoryLength = 24; // 24 observations
    uint256 public observationInterval = 1 hours;

    /// @notice Record current price (called by keeper)
    function recordPrice(address token) external {
        uint256 currentPrice = _getCurrentPrice(token);

        PriceObservation[] storage history = priceHistory[token];
        uint256 idx = historyIndex[token];

        if (history.length < maxHistoryLength) {
            history.push(PriceObservation({
                price: currentPrice,
                timestamp: uint32(block.timestamp)
            }));
        } else {
            history[idx % maxHistoryLength] = PriceObservation({
                price: currentPrice,
                timestamp: uint32(block.timestamp)
            });
        }

        historyIndex[token] = idx + 1;
    }

    /// @notice Calculate historical volatility (standard deviation of returns)
    /// @return volatilityBps Volatility in basis points
    function getHistoricalVolatility(
        address token
    ) external view returns (uint256 volatilityBps) {
        PriceObservation[] storage history = priceHistory[token];
        uint256 len = history.length;

        if (len < 2) return 0;

        // Calculate returns and their variance
        uint256 sumSquaredReturns = 0;
        uint256 count = 0;

        for (uint256 i = 1; i < len; i++) {
            uint256 prevPrice = history[i - 1].price;
            uint256 currPrice = history[i].price;

            if (prevPrice == 0) continue;

            // Return in bps: (curr - prev) / prev * 10000
            int256 returnBps;
            if (currPrice > prevPrice) {
                returnBps = int256((currPrice - prevPrice) * BPS / prevPrice);
            } else {
                returnBps = -int256((prevPrice - currPrice) * BPS / prevPrice);
            }

            sumSquaredReturns += uint256(returnBps * returnBps);
            count++;
        }

        if (count == 0) return 0;

        // Volatility = sqrt(variance)
        uint256 variance = sumSquaredReturns / count;
        volatilityBps = _sqrt(variance);
    }

    /// @notice Get min/max prices over history
    function getPriceBounds(
        address token
    ) external view returns (uint256 minPrice, uint256 maxPrice) {
        PriceObservation[] storage history = priceHistory[token];

        minPrice = type(uint256).max;
        maxPrice = 0;

        for (uint256 i = 0; i < history.length; i++) {
            uint256 price = history[i].price;
            if (price < minPrice) minPrice = price;
            if (price > maxPrice) maxPrice = price;
        }

        if (minPrice == type(uint256).max) minPrice = 0;
    }

    function _sqrt(uint256 x) internal pure returns (uint256) {
        if (x == 0) return 0;
        uint256 z = (x + 1) / 2;
        uint256 y = x;
        while (z < y) {
            y = z;
            z = (x / z + z) / 2;
        }
        return y;
    }

    function _getCurrentPrice(address token) internal view virtual returns (uint256);
}
```

### Dynamic Premium Calculator

Use volatility to adjust vault entry/exit fees:

```solidity
contract DynamicPremiumCalculator {
    uint256 constant BPS = 10000;

    uint256 public basePremiumBps = 25;     // 0.25% base
    uint256 public maxPremiumBps = 300;     // 3% max
    uint256 public volatilityMultiplier = 20; // Premium scaling factor

    /// @notice Calculate premium based on current volatility
    /// @param volatilityBps Current volatility in basis points
    /// @return premiumBps Entry/exit premium to charge
    function calculatePremium(
        uint256 volatilityBps
    ) external view returns (uint256 premiumBps) {
        // Premium = base + (volatility * multiplier / 100)
        // e.g., 3% volatility (300 bps) → 25 + (300 * 20 / 100) = 85 bps
        uint256 volPremium = volatilityBps * volatilityMultiplier / 100;

        premiumBps = basePremiumBps + volPremium;

        if (premiumBps > maxPremiumBps) {
            premiumBps = maxPremiumBps;
        }
    }

    /// @notice Premium lookup table for gas efficiency
    function getPremiumTier(
        uint256 volatilityBps
    ) external pure returns (uint256 premiumBps) {
        if (volatilityBps < 100) return 25;       // <1% vol → 0.25%
        if (volatilityBps < 300) return 50;       // 1-3% vol → 0.50%
        if (volatilityBps < 500) return 100;      // 3-5% vol → 1.00%
        if (volatilityBps < 1000) return 150;     // 5-10% vol → 1.50%
        return 300;                                // >10% vol → 3.00%
    }
}
```

### Multi-Asset Volatility Aggregator

For vaults holding multiple assets:

```solidity
contract MultiAssetVolatilityAggregator {
    uint256 constant BPS = 10000;

    struct AssetWeight {
        address token;
        uint256 weightBps;  // Weight in portfolio (sum = 10000)
    }

    /// @notice Calculate weighted portfolio volatility
    /// @param assets Array of assets with weights
    /// @param quoteToken Token to measure prices in
    /// @return aggregateVolatilityBps Weighted average volatility
    function getPortfolioVolatility(
        AssetWeight[] calldata assets,
        address quoteToken
    ) external view returns (uint256 aggregateVolatilityBps) {
        uint256 weightedSum = 0;

        for (uint256 i = 0; i < assets.length; i++) {
            uint256 assetVol = _getAssetVolatility(
                assets[i].token,
                quoteToken
            );

            weightedSum += assetVol * assets[i].weightBps;
        }

        aggregateVolatilityBps = weightedSum / BPS;
    }

    /// @notice Get maximum volatility across all assets (conservative)
    function getMaxAssetVolatility(
        address[] calldata tokens,
        address quoteToken
    ) external view returns (uint256 maxVolatilityBps, address mostVolatile) {
        maxVolatilityBps = 0;

        for (uint256 i = 0; i < tokens.length; i++) {
            uint256 vol = _getAssetVolatility(tokens[i], quoteToken);
            if (vol > maxVolatilityBps) {
                maxVolatilityBps = vol;
                mostVolatile = tokens[i];
            }
        }
    }

    function _getAssetVolatility(
        address token,
        address quoteToken
    ) internal view virtual returns (uint256);
}
```

## Calibration Guide

### Volatility Thresholds by Asset Type

| Asset Type | Normal Vol | Elevated Vol | High Vol | Extreme Vol |
|------------|------------|--------------|----------|-------------|
| Stablecoins | <0.5% | 0.5-1% | 1-2% | >2% |
| ETH/BTC | <2% | 2-5% | 5-10% | >10% |
| Large-cap alts | <3% | 3-7% | 7-15% | >15% |
| Small-cap/DeFi | <5% | 5-10% | 10-20% | >20% |

### Recommended Actions by Volatility Level

| Volatility Level | Premium Adjustment | Operations |
|------------------|-------------------|------------|
| Normal | Base premium (0.25%) | All allowed |
| Elevated | +0.25-0.5% | All allowed |
| High | +0.5-1.5% | Large ops require delay |
| Extreme | +1.5-3% or pause | Consider circuit breaker |

### TWAP Period Selection

| Volatility Environment | Recommended TWAP Window |
|------------------------|------------------------|
| Low volatility | 15-30 minutes |
| Normal | 30-60 minutes |
| High volatility | 1-4 hours |
| Crisis/attack suspected | 4-24 hours |

## Key Points

### Gas Optimization

For frequent checks, consider:

```solidity
// Cache prices when multiple operations need them
struct CachedPrices {
    uint256 spot;
    uint256 twap;
    uint256 oracle;
    uint256 timestamp;
}

mapping(address => CachedPrices) public priceCache;
uint256 public cacheTTL = 1 minutes;

function getCachedVolatility(address token) external returns (uint256) {
    CachedPrices storage cache = priceCache[token];

    if (block.timestamp > cache.timestamp + cacheTTL) {
        // Refresh cache
        cache.spot = _getSpotPrice(token);
        cache.twap = _getTwapPrice(token);
        cache.oracle = _getOraclePrice(token);
        cache.timestamp = block.timestamp;
    }

    return _calculateMaxDeviation(cache.spot, cache.twap, cache.oracle);
}
```

### False Positive Handling

During legitimate volatility (news events, liquidation cascades):

```solidity
// Allow operations with elevated premium rather than blocking
modifier volatilityAware(uint256 amount) {
    uint256 volatility = _getCurrentVolatility();

    if (volatility > extremeThreshold) {
        revert("Market too volatile");
    }

    if (volatility > highThreshold) {
        // Require premium payment
        uint256 premium = _calculatePremium(volatility, amount);
        _collectPremium(msg.sender, premium);
    }

    _;
}
```

### Oracle Health Monitoring

```solidity
function diagnoseOracle(
    address token
) external view returns (string memory diagnosis) {
    uint256 spot = _getSpotPrice(token);
    uint256 twap = _getTwapPrice(token);
    uint256 oracle = _getOraclePrice(token);

    bool spotTwapOk = _deviationOk(spot, twap, 200);
    bool spotOracleOk = _deviationOk(spot, oracle, 300);
    bool twapOracleOk = _deviationOk(twap, oracle, 200);

    if (spotTwapOk && spotOracleOk && twapOracleOk) {
        return "HEALTHY";
    }
    if (!spotOracleOk && !twapOracleOk && spotTwapOk) {
        return "ORACLE_STALE";
    }
    if (spotOracleOk && twapOracleOk && !spotTwapOk) {
        return "TWAP_LAGGING";
    }
    if (!spotOracleOk && !spotTwapOk && twapOracleOk) {
        return "SPOT_MANIPULATED";
    }
    return "HIGH_VOLATILITY";
}
```

## Real-World Examples

- [Aave Risk Parameters](https://docs.aave.com/risk/) — volatility-based LTV adjustments
- [Compound III Risk Engine](https://docs.compound.finance/) — dynamic liquidation incentives
- [Euler Oracle Health](https://github.com/euler-xyz/euler-price-oracle) — multi-source validation
- [GMX Price Deviation](https://docs.gmx.io/) — spread adjustments based on oracle deviation

## Related Patterns

- [DEX Price Oracle](./pattern-dex-pricing.md) — source of spot and TWAP prices
- [Circuit Breaker](../vaults/pattern-circuit-breaker.md) — uses volatility to pause operations
- [Dynamic Premium](../vaults/pattern-dynamic-premium.md) — adjusts fees based on volatility
- [Premium Buffer](../vaults/pattern-premium-buffer.md) — static premium for oracle risk

## References

- [Chainlink Data Quality](https://docs.chain.link/data-feeds/selecting-data-feeds)
- [Uniswap V3 Oracle Security](https://blog.uniswap.org/uniswap-v3-oracles)
- [DeFi Risk Framework (Gauntlet)](https://gauntlet.network/)
