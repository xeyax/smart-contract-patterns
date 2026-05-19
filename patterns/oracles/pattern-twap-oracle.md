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

Uniswap V2-style pools store cumulative fixed-point prices, while Uniswap V3 stores tick (log-price) accumulators that can be queried for historical points.

For V2-style accumulators:

```
price0Cumulative += reserve1 / reserve0 * secondsElapsed
price1Cumulative += reserve0 / reserve1 * secondsElapsed
TWAP = (priceCumulative_now - priceCumulative_past) / elapsed
```

The accumulator uses the previous reserve ratio over elapsed time. Periphery readers can compute a counterfactual current cumulative value without forcing a pool state update.

For V2-style sliding windows, store observations in epoch buckets and avoid overwriting the same bucket twice. A usable observation should be old enough to cover the requested window, recent enough to be inside the configured window, and paired with counterfactual current cumulative prices rather than requiring a pool sync.

For fixed-window V2 readers, initialize and gate the average before value-bearing
`consult` calls. A reader that stores zero averages until the first update should
fail closed or expose an explicit readiness flag so callers do not treat zero as
a valid price.

For V3-style accumulators:

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
    (int24 arithmeticMeanTick, uint128 harmonicMeanLiquidity) = OracleLibrary.consult(pool, twapWindow);
    require(harmonicMeanLiquidity >= minLiquidity, "low liquidity");
    
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
| **Uninitialized observation history** | TWAP silently covers a shorter period than intended or reverts | Gate reads until cardinality and oldest observation cover the full window |
| **Ignoring harmonic mean liquidity** | TWAP can include thin or zero-liquidity manipulation windows | Require minimum windowed harmonic mean liquidity |
| **Mixing V2 and V3 assumptions** | Wrong price math or readiness checks | Use cumulative-price windows for V2 pools and tick/liquidity observations for V3 pools |
| **Same-period V2 overwrite** | Oracle observation window collapses or becomes too recent | Skip updates until the next period bucket |
| **Unready fixed-window V2 average** | Default zero averages can leak into value-bearing reads | Gate `consult` until the first successful update initializes averages |
| **Wrapper timestamp masking** | A Chainlink-compatible wrapper can return `updatedAt = block.timestamp` while the underlying TWAP is unready | Check underlying readiness/cardinality and economic timestamp, not only wrapper freshness |

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

### Maturity Implied-Rate TWAP

Fixed-yield AMMs can accumulate an implied-rate value rather than a direct spot price. The reader derives PT, YT, or LP rates from the average implied rate and time remaining to expiry. In this variant, readiness checks must cover both the observation ring and the market's maturity state.

### AMM EMA Oracle

Some AMMs maintain an exponential moving average of pool state, such as a
stable-swap price oracle or crypto-pool price scale. This is useful for execution
logic and monitoring, but it is not the same as a trade-volume TWAP and should
not be promoted to a manipulation-resistant collateral oracle without separate
liquidity, update, and action-scope analysis.

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

### Execution Slippage Guard Variant

A router can use current ticks and TWAP ticks as an execution guard rather than
as a standalone collateral oracle. For multi-hop or split routes, compute a
synthetic path tick from the hops and weights, then reject execution when current
or TWAP tick deviates beyond the user or protocol bound. The guard must fail
closed if a pool lacks the observation history required for the requested window.

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

### Readiness Gate

Increasing `observationCardinalityNext` does not backfill history. A pool is ready only after enough swaps or observations have populated the ring buffer and the oldest usable observation is at least `twapWindow` seconds old.

Before using a TWAP for value-bearing operations:

- Check that current cardinality is at least the required cardinality, not just `cardinalityNext`.
- Verify the pool has an observation older than the requested window.
- Check the returned harmonic mean liquidity against a minimum threshold for value-bearing use.
- Use a separate initialization phase or circuit breaker until readiness is true.
- Reject fallback-to-shorter-window behavior unless the shorter window is explicitly configured and audited.
- For synthetic path guards, verify every hop's observation cardinality and
  weight math before treating the path-level tick as a slippage bound.

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
- [Uniswap V2](https://github.com/Uniswap/v2-core) — cumulative reserve-ratio price accumulators with counterfactual current cumulative reads in periphery
- PancakeSwap V2 periphery includes a sliding-window oracle that buckets observations by period, rejects missing or too-recent observations, and computes current cumulative prices counterfactually.
- QuickSwap/Uniswap V2 example fixed-window oracle code illustrates the need to gate `consult` until the first update initializes nonzero averages; its sliding-window example rejects missing observations.
- Pendle V2 accumulates implied-rate observations and derives PT/YT/LP rates from time-to-expiry, while its Chainlink-compatible wrapper illustrates why callers must check underlying TWAP readiness and not only `updatedAt`.
- [Euler Finance](https://docs.euler.finance/euler-protocol/getting-started/methodology/oracle-rating) — uses TWAP for price discovery
- [Angle Protocol](https://docs.angle.money/overview/oracles) — TWAP as reference price
- Uniswap swap-router contracts use synthetic path and weighted-route tick
  guards for slippage checks, including observation-cardinality failure tests, in
  `/private/tmp/defillama-source/Uniswap__swap-router-contracts/contracts/base/OracleSlippage.sol:17`
  and `/private/tmp/defillama-source/Uniswap__swap-router-contracts/test/OracleSlippage.spec.ts:339`.
- Curve StableSwap NG and Curve Crypto maintain AMM EMA/oracle state for pool
  execution and monitoring in `/private/tmp/defillama-source/curvefi__stableswap-ng/contracts/main/CurveStableSwapNG.vy:1295-1461`,
  `/private/tmp/defillama-source/curvefi__curve-crypto-contract/contracts/two/CurveCryptoSwap2.vy:538-607`,
  and `/private/tmp/defillama-source/curvefi__curve-crypto-contract/contracts/two/CurveCryptoSwap2.vy:610-721`; this is AMM state evidence, not a standalone collateral oracle guarantee.

## Related Patterns

- [Multi-hop Price](./pattern-multihop-price.md) — combine TWAP across multiple pools
- [Multi-Source Validation](./pattern-multi-source-validation.md) — cross-check TWAP with other sources
- [DEX Spot Price](./pattern-dex-spot-price.md) — alternative with different trade-offs
- [Chainlink Integration](./pattern-chainlink-integration.md) — off-chain alternative

## References

- [Uniswap V3 Oracle Documentation](https://docs.uniswap.org/concepts/protocol/oracle)
- [Uniswap V3 TWAP Deep Dive](https://blog.uniswap.org/uniswap-v3-oracles)
- [OracleLibrary.sol](https://github.com/Uniswap/v3-periphery/blob/main/contracts/libraries/OracleLibrary.sol)
- [Uniswap V2 Oracle Library](https://github.com/Uniswap/v2-periphery/blob/master/contracts/libraries/UniswapV2OracleLibrary.sol)
