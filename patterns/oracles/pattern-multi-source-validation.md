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

### Time-Bound Warning State

Some systems deliberately distinguish short-lived source disagreement from a hard
oracle failure. A primary/secondary divergence can enter a warning state for a
bounded period, but value-increasing operations should fail once the warning
window expires or if historical bounds and freshness checks are missing.

```solidity
function validateDivergence(uint256 primary, uint256 secondary) internal {
    bool closeEnough = _deviationOk(primary, secondary, maxWarningDeviationBps);
    if (closeEnough) {
        warningStartedAt = 0;
        return;
    }

    if (warningStartedAt == 0) {
        warningStartedAt = block.timestamp;
        emit OracleWarning(primary, secondary);
        return;
    }

    require(block.timestamp - warningStartedAt <= maxWarningDuration, "oracle divergence");
}
```

The warning state should not bypass min/max price bounds, freshness checks, or
history-span requirements. It is a grace period for operator response, not proof
that either source is safe.

### Bounded Agreement Aggregation

Some lending oracles cap each asset to at most three primary sources and use only
sources that return successfully. One source is accepted as a fallback, two
sources must agree within a configured deviation before averaging, and three
sources either return the median when all adjacent sorted prices agree or average
the agreeing adjacent pair.

This is simpler than diagnosing source type, but it needs tight source-count and
deviation bounds. A lone valid source is availability, not high confidence.

### Fresh Most-Recent Agreement Variant

Some Solana oracle systems validate all configured sources for freshness and
deviation, then pick the most recent source among the agreeing set. This reduces
latency versus averaging every source, but it is fail-closed: a stale or
divergent minority source can halt the composite rather than being silently
ignored.

### Off-Chain Spot Aggregation Boundary

Aggregating many spot sources can improve off-chain routing and monitoring, but
it is not on-chain multi-source validation when every source can be manipulated
inside the same transaction. Keep off-chain quote aggregators out of value-moving
oracle paths unless they add TWAP, signed reports, delayed settlement, or another
manipulation-resistant boundary.

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
- If using a warning state, cap both maximum deviation and maximum warning duration, then fail closed after expiry.
- If accepting a single valid source, make that fallback explicit in action-scoped policy and avoid treating it as equal to multi-source agreement.
- Weighted averaging is not validation by itself. If all sources are simply averaged, still enforce per-source freshness plus deviation, quorum, median, or adjacent-agreement rules before treating the output as validated.
- Off-chain spot aggregation should remain an advisory input unless the on-chain
  consumer has independent manipulation resistance.

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
- NAVI validates primary/secondary oracle divergence with warning and rejection states in `/private/tmp/defillama-source/naviprotocol__navi-smart-contracts/oracle/sources/oracle_pro.move` and `oracle/sources/strategy.move`.
- Liquity V1's `PriceFeed.sol` fallback and last-good-price state machine provides additional evidence that source disagreement needs explicit status transitions instead of silent fallback.
- Alpha Homora V2's `AggregatorOracle` caps primary sources at three, sorts valid prices, averages agreeing pairs, returns the median when all three agree, and reverts when no pair is within deviation in `/private/tmp/defillama-source/AlphaFinanceLab__alpha-homora-v2-contract/contracts/oracle/AggregatorOracle.sol`.
- Satoshi Core's weighted Chainlink aggregator checks source freshness but illustrates why averaging multiple sources should not be described as validation unless it also enforces deviation or quorum semantics.
- Kamino Scope's most-recent oracle variants check source freshness and deviation before selecting the most recent agreeing value, with capped variants preserving the same fail-closed semantics in `/private/tmp/defillama-source/Kamino-Finance_scope/programs/scope/src/oracles/most_recent_of.rs`, `oracles/capped_most_recent_of.rs`, and `utils/source_entries.rs`.
- 1inch Spot Price Aggregator is explicitly off-chain-only despite aggregating
  DEX sources, and its contract-level warning preserves the spot-manipulation
  boundary in `/private/tmp/defillama-source/1inch__spot-price-aggregator/README.md:11`
  and `/private/tmp/defillama-source/1inch__spot-price-aggregator/contracts/OffchainOracle.sol:241`.

## Related Patterns

- [TWAP Oracle](./pattern-twap-oracle.md) — one of the sources to validate
- [Chainlink Integration](./pattern-chainlink-integration.md) — another source to validate
- [DEX Spot Price](./pattern-dex-spot-price.md) — third source for triangulation

## References

- [Chainlink: Using Multiple Oracles](https://docs.chain.link/data-feeds/using-multiple-oracles)
- [Oracle Security Best Practices](https://blog.openzeppelin.com/secure-oracle-design)
