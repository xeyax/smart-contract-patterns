# DEX Price Oracle

> Calculate asset prices using DEX pools: spot price, TWAP, and multi-hop routing when direct stablecoin pools don't exist.

## Metadata

| Property | Value |
|----------|-------|
| Category | oracles |
| Tags | oracle, price, twap, spot, dex, uniswap, multi-hop |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Need on-chain price data without external oracle dependency
- Chainlink feed unavailable for the asset
- Want manipulation-resistant price (TWAP)
- Asset only has liquidity paired with ETH, not stablecoins
- Building vault NAV calculation or liquidation logic

## Avoid When

- Chainlink feed exists and is reliable (simpler, battle-tested)
- Pool liquidity is too low (easy to manipulate)
- Need sub-second price updates (TWAP lags by design)
- Asset has no DEX liquidity at all

## Trade-offs

**Pros:**
- Fully on-chain, no external dependencies
- TWAP is manipulation-resistant (requires sustained capital)
- Works for any token with DEX liquidity
- Multi-hop extends coverage to most tokens

**Cons:**
- TWAP lags during high volatility
- Multi-hop compounds pricing errors
- Requires sufficient pool liquidity
- Gas cost for oracle queries

## How It Works

### Price Types

```
┌─────────────────────────────────────────────────────────────┐
│                      DEX Price Types                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  SPOT PRICE          TWAP                ORACLE (External)  │
│  ┌─────────┐        ┌─────────┐          ┌─────────┐       │
│  │ Current │        │ Average │          │Chainlink│       │
│  │ block   │        │ over    │          │  feed   │       │
│  │ price   │        │ period  │          │         │       │
│  └─────────┘        └─────────┘          └─────────┘       │
│       │                  │                    │             │
│       ▼                  ▼                    ▼             │
│  Manipulable       Manipulation-         Independent       │
│  (flash loan)      resistant             source            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Multi-hop Routing

When direct pool doesn't exist:

```
Token A ──────────────────────────────────X──────────────────> USDC
         (no direct pool)

Token A ───(Pool 1)───> WETH ───(Pool 2)───> USDC
            price₁               price₂

Final Price = price₁ × price₂
```

## Implementation

### Core Interface

```solidity
interface IDexPriceOracle {
    /// @notice Get instantaneous spot price
    /// @param base Token to price
    /// @param quote Token to price in (e.g., USDC)
    /// @return price Price of 1 base token in quote tokens (quote decimals)
    function getSpotPrice(
        address base,
        address quote
    ) external view returns (uint256 price);

    /// @notice Get time-weighted average price
    /// @param base Token to price
    /// @param quote Token to price in
    /// @param period TWAP window in seconds
    /// @return price TWAP of 1 base token in quote tokens
    function getTWAP(
        address base,
        address quote,
        uint32 period
    ) external view returns (uint256 price);

    /// @notice Get price with automatic routing
    /// @param base Token to price
    /// @param quote Token to price in
    /// @param useTwap Use TWAP (true) or spot (false)
    /// @param twapPeriod TWAP window if useTwap is true
    /// @return price Price of 1 base token in quote tokens
    function getPrice(
        address base,
        address quote,
        bool useTwap,
        uint32 twapPeriod
    ) external view returns (uint256 price);
}
```

### Spot Price

Spot price reflects current pool state — can be manipulated within a single transaction.

```solidity
contract DexSpotOracle {
    uint256 constant PRECISION = 1e18;

    /// @notice Get spot price from pool reserves/state
    function getSpotPrice(
        address base,
        address quote
    ) external view returns (uint256) {
        address pool = _getPool(base, quote);
        require(pool != address(0), "No pool");

        return _getSpotPriceFromPool(pool, base, quote);
    }

    /// @dev Abstract: get price from specific pool implementation
    /// For V2-style: price = reserveQuote / reserveBase
    /// For V3-style: price = sqrtPriceX96² / 2¹⁹²
    function _getSpotPriceFromPool(
        address pool,
        address base,
        address quote
    ) internal view virtual returns (uint256);

    function _getPool(
        address tokenA,
        address tokenB
    ) internal view virtual returns (address);
}
```

### TWAP (Time-Weighted Average Price)

TWAP smooths price over time, making manipulation expensive.

```solidity
contract DexTwapOracle {
    uint256 constant PRECISION = 1e18;

    /// @notice Get TWAP over specified period
    /// @param period Time window in seconds (e.g., 1800 for 30 min)
    function getTWAP(
        address base,
        address quote,
        uint32 period
    ) external view returns (uint256) {
        address pool = _getPool(base, quote);
        require(pool != address(0), "No pool");
        require(period > 0, "Period must be > 0");

        return _getTwapFromPool(pool, base, quote, period);
    }

    /// @dev Abstract: get TWAP from specific pool implementation
    /// V2-style: requires external cumulative price tracking
    /// V3-style: uses built-in oracle with tick accumulators
    function _getTwapFromPool(
        address pool,
        address base,
        address quote,
        uint32 period
    ) internal view virtual returns (uint256);

    function _getPool(
        address tokenA,
        address tokenB
    ) internal view virtual returns (address);
}
```

### TWAP Window Selection

| Window | Use Case | Trade-off |
|--------|----------|-----------|
| 5-15 min | High-frequency operations | More responsive, less resistant |
| 30 min | Standard vault operations | Good balance |
| 1-4 hours | Lending liquidations | Very resistant, may lag |
| 24 hours | Long-term valuations | Maximum resistance, significant lag |

**Rule of thumb:** Window should be longer than attacker can sustain position profitably.

### Multi-hop Price Router

```solidity
contract MultiHopPriceRouter {
    uint256 constant PRECISION = 1e18;

    address public immutable WETH;
    address public immutable USDC;

    // Common intermediate tokens for routing
    address[] public intermediates;

    constructor(address weth, address usdc) {
        WETH = weth;
        USDC = usdc;
        intermediates.push(weth);
        intermediates.push(usdc);
    }

    /// @notice Get price with automatic route finding
    function getPrice(
        address base,
        address quote,
        bool useTwap,
        uint32 twapPeriod
    ) external view returns (uint256) {
        // Try direct pool first
        if (_hasLiquidity(base, quote)) {
            return useTwap
                ? _getTwap(base, quote, twapPeriod)
                : _getSpot(base, quote);
        }

        // Try routing through intermediates
        for (uint i = 0; i < intermediates.length; i++) {
            address intermediate = intermediates[i];

            if (intermediate == base || intermediate == quote) continue;

            if (_hasLiquidity(base, intermediate) &&
                _hasLiquidity(intermediate, quote)) {

                uint256 price1 = useTwap
                    ? _getTwap(base, intermediate, twapPeriod)
                    : _getSpot(base, intermediate);

                uint256 price2 = useTwap
                    ? _getTwap(intermediate, quote, twapPeriod)
                    : _getSpot(intermediate, quote);

                return price1 * price2 / PRECISION;
            }
        }

        revert("No pricing route available");
    }

    /// @dev Check if pool has sufficient liquidity
    function _hasLiquidity(
        address tokenA,
        address tokenB
    ) internal view virtual returns (bool);

    function _getSpot(
        address base,
        address quote
    ) internal view virtual returns (uint256);

    function _getTwap(
        address base,
        address quote,
        uint32 period
    ) internal view virtual returns (uint256);
}
```

### Pricing with Fallback

```solidity
contract RobustPriceOracle {
    uint256 constant PRECISION = 1e18;
    uint256 constant BPS = 10000;

    uint256 public maxDeviationBps = 500; // 5%

    /// @notice Get price with cross-validation
    /// @return price The validated price
    /// @return confidence true if sources agree within threshold
    function getPriceWithConfidence(
        address base,
        address quote
    ) external view returns (uint256 price, bool confidence) {
        uint256 spot = _getSpotPrice(base, quote);
        uint256 twap = _getTwapPrice(base, quote, 30 minutes);

        uint256 deviation = _calculateDeviation(spot, twap);
        confidence = deviation <= maxDeviationBps;

        // Return TWAP as more manipulation-resistant
        price = twap;
    }

    /// @notice Get price preferring external oracle with DEX fallback
    function getPriceWithFallback(
        address base,
        address quote
    ) external view returns (uint256) {
        // Try Chainlink first
        (uint256 oraclePrice, bool fresh) = _tryGetOraclePrice(base, quote);
        if (fresh) {
            return oraclePrice;
        }

        // Fallback to DEX TWAP
        return _getTwapPrice(base, quote, 30 minutes);
    }

    function _calculateDeviation(
        uint256 a,
        uint256 b
    ) internal pure returns (uint256) {
        if (a > b) {
            return (a - b) * BPS / b;
        }
        return (b - a) * BPS / a;
    }

    // Abstract functions
    function _getSpotPrice(address base, address quote) internal view virtual returns (uint256);
    function _getTwapPrice(address base, address quote, uint32 period) internal view virtual returns (uint256);
    function _tryGetOraclePrice(address base, address quote) internal view virtual returns (uint256 price, bool fresh);
}
```

## Key Points

### Multi-hop Error Accumulation

Each hop introduces pricing error:
- Spot: slippage + potential manipulation
- TWAP: lag + observation granularity

```
2-hop error ≈ error₁ + error₂ + (error₁ × error₂)

Example: 0.5% + 0.5% + 0.0025% ≈ 1% total error
```

**Mitigation:** Use wider deviation thresholds for multi-hop prices.

### Liquidity Requirements

Minimum liquidity for reliable pricing:

| Asset Type | Min Liquidity | Rationale |
|------------|---------------|-----------|
| Major (ETH, BTC) | $1M+ | High-value operations |
| Mid-cap | $100K+ | Standard vault use |
| Long-tail | $10K+ | Small allocations only |

### TWAP Manipulation Cost (PoS)

In Proof of Stake, manipulation is harder but possible:

```
Cost to manipulate = pool_fee × manipulation_amount × blocks_held

Example: 0.3% fee, $10M manipulation, 2 blocks
Cost ≈ $60K + opportunity cost + revert risk
```

**Defense:** Use TWAP windows covering multiple blocks (30+ min recommended).

### Decimal Handling

Always normalize to common precision:

```solidity
function _normalizePrice(
    uint256 rawPrice,
    uint8 baseDecimals,
    uint8 quoteDecimals
) internal pure returns (uint256) {
    // Normalize to 18 decimals
    if (baseDecimals > quoteDecimals) {
        return rawPrice * 10**(baseDecimals - quoteDecimals);
    } else if (quoteDecimals > baseDecimals) {
        return rawPrice / 10**(quoteDecimals - baseDecimals);
    }
    return rawPrice;
}
```

## Real-World Examples

- [Uniswap V3 Oracle](https://docs.uniswap.org/concepts/protocol/oracle) — built-in TWAP with geometric mean
- [Euler Price Oracle](https://github.com/euler-xyz/euler-price-oracle) — modular adapter system
- [DittoETH Oracle](https://dittoeth.com/technical/oracles) — Chainlink primary with TWAP fallback
- [Mean Finance TWAP](https://github.com/Mean-Finance/uniswap-v3-oracle) — V3 TWAP wrapper

## Related Patterns

- [Circuit Breaker](../vaults/pattern-circuit-breaker.md) — uses TWAP as reference price for deviation check
- [Dynamic Premium](../vaults/pattern-dynamic-premium.md) — uses price volatility to adjust fees
- [Oracle Arbitrage Risk](../vaults/risk-oracle-arbitrage.md) — the problem DEX oracles help solve

## References

- [Uniswap V3 TWAP Oracles in Proof of Stake](https://blog.uniswap.org/uniswap-v3-oracles)
- [Chaos Labs: TWAP Deep Dive](https://chaoslabs.xyz/posts/chaos-labs-uniswap-v3-twap-deep-dive-pt-1)
- [TWAP vs VWAP (Chainlink)](https://chain.link/education-hub/twap-vs-vwap)
- [Euler Price Oracle Docs](https://docs.euler.finance/concepts/core/price-oracles/)
