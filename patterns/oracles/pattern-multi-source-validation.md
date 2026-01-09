# Multi-Source Validation

> Cross-check prices from multiple oracle sources to detect anomalies and identify which source is malfunctioning.

## Metadata

| Property | Value |
|----------|-------|
| Category | oracles |
| Tags | oracle, validation, cross-check, anomaly-detection, safety |
| Complexity | Medium |
| Gas Efficiency | Low |
| Audit Risk | Low |

## Use When

- High-value operations depend on oracle price
- Need to distinguish between oracle types of failures
- Want defense-in-depth for price feeds
- Building circuit breaker or safety mechanism

## Avoid When

- Gas cost is critical (multiple oracle reads)
- Only one reliable price source exists
- Low-value operations where precision is less important
- Real-time response is required (latency from multiple reads)

## Trade-offs

**Pros:**
- Can identify WHICH source is wrong
- Graceful degradation when one source fails
- Higher confidence in price accuracy
- Defense against single oracle failure

**Cons:**
- Higher gas cost (multiple reads)
- More complex logic
- All sources must have sufficient liquidity/availability
- May increase latency

## How It Works

Compare three price sources:
1. **Off-chain Oracle** (Chainlink) — independent, but can be stale
2. **TWAP** — manipulation-resistant, but lags
3. **DEX Spot** — real-time, but manipulable

By comparing all three, you can diagnose the issue:

```
┌──────────────────────────────────────────────────────────────┐
│                    Price Source Comparison                    │
├──────────────┬──────────────┬──────────────┬─────────────────┤
│ Oracle/TWAP  │ Oracle/Spot  │ TWAP/Spot    │ Interpretation  │
├──────────────┼──────────────┼──────────────┼─────────────────┤
│     ✅       │     ✅       │     ✅       │ All agree       │
│     ❌       │     ❌       │     ✅       │ Oracle stale    │
│     ✅       │     ❌       │     ❌       │ Spot manipulated│
│     ❌       │     ✅       │     ❌       │ TWAP lagging    │
│     ❌       │     ❌       │     ❌       │ High volatility │
└──────────────┴──────────────┴──────────────┴─────────────────┘
```

## Requirements Satisfied

This pattern satisfies [Oracle Reliability Requirements](./req-oracle-reliability.md):
- **R1: Freshness** — detects stale oracle
- **R2: Accuracy** — cross-validates accuracy
- **R3: Manipulation Resistance** — detects spot manipulation
- **R4: Availability** — fallback when one source fails

## Implementation

```solidity
contract MultiSourceOracle {
    uint256 public oracleTwapThresholdBps = 200;   // 2%
    uint256 public oracleSpotThresholdBps = 300;   // 3%
    uint256 public twapSpotThresholdBps = 200;     // 2%
    uint256 constant BPS = 10000;

    enum PriceStatus {
        AllAgree,        // Safe to use any
        OracleStale,     // Trust TWAP/Spot
        SpotManipulated, // Trust Oracle/TWAP
        TwapLagging,     // Trust Oracle/Spot
        HighVolatility   // Pause operations
    }

    function validatePrice() public view returns (PriceStatus, uint256 price) {
        uint256 oraclePrice = _getChainlinkPrice();
        uint256 twapPrice = _getUniswapTWAP(30 minutes);
        uint256 spotPrice = _getUniswapSpot();

        bool oracleVsTwap = _deviationOk(oraclePrice, twapPrice, oracleTwapThresholdBps);
        bool oracleVsSpot = _deviationOk(oraclePrice, spotPrice, oracleSpotThresholdBps);
        bool twapVsSpot = _deviationOk(twapPrice, spotPrice, twapSpotThresholdBps);

        if (oracleVsTwap && oracleVsSpot && twapVsSpot) {
            // All sources agree — use oracle (most gas efficient for repeated reads)
            return (PriceStatus.AllAgree, oraclePrice);
        }

        if (!oracleVsTwap && !oracleVsSpot && twapVsSpot) {
            // TWAP and Spot agree, Oracle differs → Oracle is stale
            return (PriceStatus.OracleStale, twapPrice);
        }

        if (oracleVsTwap && !oracleVsSpot && !twapVsSpot) {
            // Oracle and TWAP agree, Spot differs → Spot is manipulated
            return (PriceStatus.SpotManipulated, oraclePrice);
        }

        if (!oracleVsTwap && oracleVsSpot && !twapVsSpot) {
            // Oracle and Spot agree, TWAP differs → TWAP is lagging
            return (PriceStatus.TwapLagging, oraclePrice);
        }

        // Nothing agrees — high volatility or coordinated attack
        return (PriceStatus.HighVolatility, 0);
    }

    function _deviationOk(uint256 a, uint256 b, uint256 maxBps) internal pure returns (bool) {
        uint256 diff = a > b ? a - b : b - a;
        uint256 maxDiff = (a * maxBps) / BPS;
        return diff <= maxDiff;
    }

    // --- Price source implementations ---
    function _getChainlinkPrice() internal view returns (uint256);
    function _getUniswapTWAP(uint32 window) internal view returns (uint256);
    function _getUniswapSpot() internal view returns (uint256);
}
```

### With Circuit Breaker Integration

```solidity
contract VaultWithMultiSourceOracle is MultiSourceOracle {

    modifier priceValidated() {
        (PriceStatus status, uint256 price) = validatePrice();

        if (status == PriceStatus.HighVolatility) {
            revert("Circuit breaker: price sources disagree");
        }

        // Log anomalies but continue
        if (status != PriceStatus.AllAgree) {
            emit PriceAnomaly(status, price);
        }

        _;
    }

    function deposit(uint256 amount) external priceValidated {
        // ... deposit logic using validated price
    }
}
```

### Weighted Consensus

For more nuanced decisions, weight sources by reliability:

```solidity
function getConsensusPrice() public view returns (uint256) {
    uint256 oraclePrice = _getChainlinkPrice();
    uint256 twapPrice = _getUniswapTWAP(30 minutes);
    uint256 spotPrice = _getUniswapSpot();

    // Weight: Oracle 40%, TWAP 40%, Spot 20%
    return (oraclePrice * 40 + twapPrice * 40 + spotPrice * 20) / 100;
}
```

## Interpretation Table

| Oracle vs TWAP | Oracle vs Spot | TWAP vs Spot | Diagnosis | Recommended Action |
|----------------|----------------|--------------|-----------|-------------------|
| ✅ | ✅ | ✅ | All sources agree | Allow operation |
| ❌ | ❌ | ✅ | Oracle stale | Use TWAP, alert |
| ✅ | ❌ | ❌ | Spot manipulated | Use Oracle/TWAP |
| ❌ | ✅ | ❌ | TWAP lagging | Use Oracle/Spot |
| ❌ | ❌ | ❌ | High volatility or attack | Pause operations |

## Threshold Calibration

| Comparison | Suggested Threshold | Rationale |
|------------|---------------------|-----------|
| Oracle vs TWAP | 2% | Both should track closely |
| Oracle vs Spot | 3% | Spot is more volatile |
| TWAP vs Spot | 2% | On-chain sources should agree |

**Asset-specific adjustments:**
- Stablecoins: tighten all thresholds to 0.5-1%
- Volatile assets: loosen to 5-10%

## Gas Optimization

Reading three sources is expensive. Optimize for common case:

```solidity
function getOptimizedPrice() public view returns (uint256) {
    uint256 oraclePrice = _getChainlinkPrice();
    uint256 twapPrice = _getUniswapTWAP(30 minutes);

    // Only read spot if Oracle/TWAP disagree
    if (_deviationOk(oraclePrice, twapPrice, 200)) {
        return oraclePrice;  // Fast path: 2 reads
    }

    // Slow path: need spot to diagnose
    uint256 spotPrice = _getUniswapSpot();
    // ... full validation logic
}
```

## Real-World Examples

- [Aave Price Oracle](https://docs.aave.com/developers/core-contracts/aaveoracle) — fallback oracle mechanism
- [Compound Price Feed](https://docs.compound.finance/v2/prices/) — multi-source validation
- [MakerDAO Medianizer](https://docs.makerdao.com/smart-contract-modules/oracle-module) — median of multiple sources

## Related Patterns

- [TWAP Oracle](./pattern-twap-oracle.md) — one of the sources to validate
- [Chainlink Integration](./pattern-chainlink-integration.md) — another source to validate
- [DEX Spot Price](./pattern-dex-spot-price.md) — third source for triangulation

## References

- [Chainlink: Using Multiple Oracles](https://docs.chain.link/data-feeds/using-multiple-oracles)
- [Oracle Security Best Practices](https://blog.openzeppelin.com/secure-oracle-design)

