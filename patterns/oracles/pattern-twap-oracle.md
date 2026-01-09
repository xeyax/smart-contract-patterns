# TWAP Oracle

> Time-Weighted Average Price from DEX pools — manipulation-resistant on-chain price discovery.

## Metadata

| Property | Value |
|----------|-------|
| Category | oracles |
| Tags | oracle, twap, uniswap, price, manipulation-resistant |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Need manipulation-resistant on-chain price
- Asset has sufficient DEX liquidity
- Can tolerate price lag during volatility
- Want fully decentralized price source

## Avoid When

- Need real-time price (use spot with caution)
- Asset has low DEX liquidity
- Price changes rapidly and lag is unacceptable
- Gas cost of oracle read is critical

## Trade-offs

**Pros:**
- Resistant to single-block manipulation
- Fully on-chain, no external dependencies
- Flash loan attacks don't affect TWAP
- Transparent and verifiable

**Cons:**
- Lags behind spot price during volatility
- Requires sufficient pool liquidity
- Higher gas than simple storage read
- Observation array may not cover desired window

## How It Works

TWAP calculates the average price over a time window by accumulating price-seconds:

```
TWAP = (cumulativePrice_now - cumulativePrice_past) / (time_now - time_past)
```

Uniswap V3 stores tick (log-price) accumulators that can be queried for any historical point:

```
tickCumulative grows by: currentTick × secondsElapsed
```

To get TWAP:
1. Query `observe()` for two timestamps
2. Calculate tick difference
3. Convert tick to price

## Requirements Satisfied

This pattern satisfies [Oracle Reliability Requirements](./req-oracle-reliability.md):
- **R1: Freshness** — uses recent on-chain data
- **R2: Accuracy** — reflects actual trading activity
- **R3: Manipulation Resistance** — time-weighting defeats single-block attacks

## Implementation

### Using OracleLibrary (Recommended)

Use Uniswap's official [OracleLibrary](https://github.com/Uniswap/v3-periphery/blob/main/contracts/libraries/OracleLibrary.sol):

```solidity
import {OracleLibrary} from "@uniswap/v3-periphery/contracts/libraries/OracleLibrary.sol";

function getTWAPPrice(address pool, uint32 twapWindow) external view returns (uint256) {
    (int24 arithmeticMeanTick, ) = OracleLibrary.consult(pool, twapWindow);
    
    // Convert tick to price — use OracleLibrary.getQuoteAtTick
    return OracleLibrary.getQuoteAtTick(arithmeticMeanTick, baseAmount, baseToken, quoteToken);
}
```

**Key functions from Uniswap libraries:**
- [`OracleLibrary.consult()`](https://github.com/Uniswap/v3-periphery/blob/main/contracts/libraries/OracleLibrary.sol#L28) — get TWAP tick with correct rounding
- [`OracleLibrary.getQuoteAtTick()`](https://github.com/Uniswap/v3-periphery/blob/main/contracts/libraries/OracleLibrary.sol#L49) — convert tick to price with overflow protection
- [`TickMath.getSqrtRatioAtTick()`](https://github.com/Uniswap/v3-core/blob/main/contracts/libraries/TickMath.sol#L23) — tick to sqrtPriceX96

### Custom Implementation (If Not Using Libraries)

If you need custom implementation, the critical fix is **tick rounding**:

```solidity
function _getTwapTick(address pool, uint32 period) internal view returns (int24) {
    uint32[] memory secondsAgos = new uint32[](2);
    secondsAgos[0] = period;
    secondsAgos[1] = 0;

    (int56[] memory tickCumulatives,) = IUniswapV3Pool(pool).observe(secondsAgos);
    int56 tickDelta = tickCumulatives[1] - tickCumulatives[0];
    
    int24 tick = int24(tickDelta / int56(uint56(period)));

    // CRITICAL: Round to negative infinity (Solidity truncates toward zero)
    if (tickDelta < 0 && (tickDelta % int56(uint56(period)) != 0)) {
        tick--;
    }

    return tick;
}
```

For tick-to-price conversion, copy [TickMath.getSqrtRatioAtTick()](https://github.com/Uniswap/v3-core/blob/main/contracts/libraries/TickMath.sol#L23) and handle overflow when squaring (check `sqrtRatioX96 <= type(uint128).max` before squaring).

## Common Pitfalls

| Pitfall | Impact | Solution |
|---------|--------|----------|
| **Wrong tick rounding** | ~0.01% systematic error on negative ticks | Use floor division: `if (tickDelta < 0 && tickDelta % period != 0) tick--` |
| **Overflow when squaring sqrtRatioX96** | Revert on extreme ticks | Check `sqrtRatioX96 <= type(uint128).max` before squaring |
| **Wrong token order** | Inverted prices | Verify which token is token0 in the pool |
| **Decimal mismatch** | Orders of magnitude error | Normalize all prices to consistent decimals |

Use [OracleLibrary](https://github.com/Uniswap/v3-periphery/blob/main/contracts/libraries/OracleLibrary.sol) to avoid most of these issues.

## Calibration

| Use Case | Suggested Window | Rationale |
|----------|------------------|-----------|
| Lending liquidations | 30 min - 1 hour | Balance manipulation resistance vs. responsiveness |
| Vault NAV | 10-30 min | Moderate lag acceptable |
| Circuit breaker reference | 5-15 min | Quick detection of deviation |
| Governance voting | 1-7 days | Long-term value matters |

**Window Trade-off:**
- **Longer window** → more manipulation resistant, more lag
- **Shorter window** → less lag, easier to manipulate

## Variations

### Geometric Mean TWAP

More accurate for volatile assets (Uniswap V3 uses this):

```solidity
// Uniswap V3 accumulates log(price), so the result is geometric mean
geometricMeanPrice = 1.0001^(averageTick)
```

### Weighted TWAP

Give more weight to recent observations:

```solidity
function getWeightedTWAP() public view returns (uint256) {
    // Query multiple points and weight by recency
    uint256 recentPrice = _getTWAP(5 minutes);
    uint256 olderPrice = _getTWAP(30 minutes);

    // 70% recent, 30% older
    return (recentPrice * 70 + olderPrice * 30) / 100;
}
```

## Observation Array Requirements

Uniswap V3 pools have a limited observation array. Ensure sufficient history:

```solidity
function ensureObservationCapacity(address pool, uint16 minCardinality) external {
    IUniswapV3Pool(pool).increaseObservationCardinalityNext(minCardinality);
}
```

**Cardinality needed:**
- For 30-min TWAP: ~30 observations (assuming 1 trade/min average)
- Default is often 1 — must be increased!

## Attack Vectors

### Insufficient Liquidity

**Risk:** Low liquidity pools can be manipulated even with TWAP.

**Mitigation:** Require minimum liquidity threshold before trusting TWAP.

### Short Observation History

**Risk:** Pool doesn't have enough observations for desired window.

**Mitigation:** Check cardinality and increase if needed; fall back to shorter window.

### Multi-Block Manipulation

**Risk:** Attacker maintains manipulation across many blocks.

**Mitigation:** Use longer TWAP window; combine with other sources.

## Real-World Examples

- [Uniswap V3 Oracle](https://docs.uniswap.org/concepts/protocol/oracle) — native TWAP implementation
- [Euler Finance](https://docs.euler.finance/euler-protocol/getting-started/methodology/oracle-rating) — uses TWAP for price discovery
- [Angle Protocol](https://docs.angle.money/overview/oracles) — TWAP as reference price

## Related Patterns

- [Multi-hop Price](./pattern-multihop-price.md) — combine TWAP across multiple pools
- [Multi-Source Validation](./pattern-multi-source-validation.md) — cross-check TWAP with other sources
- [DEX Spot Price](./pattern-dex-spot-price.md) — alternative with different trade-offs
- [Chainlink Integration](./pattern-chainlink-integration.md) — off-chain alternative

## References

- [Uniswap V3 Oracle Documentation](https://docs.uniswap.org/concepts/protocol/oracle)
- [Uniswap V3 TWAP Deep Dive](https://blog.uniswap.org/uniswap-v3-oracles)
- [OracleLibrary.sol](https://github.com/Uniswap/v3-periphery/blob/main/contracts/libraries/OracleLibrary.sol)

