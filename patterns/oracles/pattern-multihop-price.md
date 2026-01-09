# Multi-hop Price

> Derive token price in USD through an intermediate base asset when no direct token/stable pool exists.

## Metadata

| Property | Value |
|----------|-------|
| Category | oracles |
| Tags | oracle, multihop, price, routing, long-tail |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Token has no direct pool against stablecoins
- Token has liquidity against major assets (WETH, WBTC)
- Need USD-denominated price for long-tail tokens
- Building circuit breaker or reference price check

## Avoid When

- Direct token/stable pool exists with sufficient liquidity
- Base asset pools also lack liquidity
- Single oracle source is acceptable
- Gas cost is critical (two pool reads)

## Trade-offs

**Pros:**
- Enables pricing for tokens without stable pools
- Uses existing DEX liquidity
- Fully on-chain, no external dependencies
- Can combine with TWAP for manipulation resistance

**Cons:**
- Two price sources = two points of failure
- Error compounds across hops
- Requires reliable base asset pools
- More complex implementation

## How It Works

Calculate price through an intermediate "bridge" asset:

```
P(token/USD) = P(token/base) × P(base/USD)
```

Where:
- `base` is a highly liquid asset (WETH preferred, WBTC fallback)
- `P(token/base)` comes from token/WETH pool
- `P(base/USD)` comes from WETH/USDC pool

```
┌─────────┐      ┌─────────┐      ┌─────────┐
│  TOKEN  │──────│  WETH   │──────│  USDC   │
└─────────┘      └─────────┘      └─────────┘
     Pool 1           Pool 2
   token/WETH       WETH/USDC
```

## Requirements Satisfied

This pattern satisfies [Oracle Reliability Requirements](./req-oracle-reliability.md):
- **R1: Freshness** — uses real-time or TWAP data
- **R2: Accuracy** — reflects actual trading routes
- **R3: Manipulation Resistance** — when combined with TWAP

## Implementation

> **Important:** For TWAP tick calculation and price conversion, see [TWAP Oracle](./pattern-twap-oracle.md).

### Core Logic

```solidity
function getTokenPriceInUSD() external view returns (uint256) {
    // Get prices from each hop using OracleLibrary
    uint256 tokenInBase = OracleLibrary.getQuoteAtTick(
        _getTwapTick(tokenBasePool), baseAmount, token, baseToken
    );
    uint256 baseInUSD = OracleLibrary.getQuoteAtTick(
        _getTwapTick(baseStablePool), baseAmount, baseToken, stableToken
    );

    // Normalize to consistent decimals and combine
    return _normalize(tokenInBase) * _normalize(baseInUSD) / 1e18;
}
```

### With Fallback Route

```solidity
function getTokenPriceInUSD() external view returns (uint256) {
    // Try WETH route first
    if (_hasLiquidity(tokenWETHPool)) {
        return _getPriceViaRoute(tokenWETHPool, wethUSDCPool);
    }
    // Fallback to WBTC route
    if (_hasLiquidity(tokenWBTCPool)) {
        return _getPriceViaRoute(tokenWBTCPool, wbtcUSDCPool);
    }
    revert("No valid price route");
}

function _hasLiquidity(address pool) internal view returns (bool) {
    return IUniswapV3Pool(pool).liquidity() >= minLiquidityThreshold;
}
```

## Common Pitfalls

Multi-hop amplifies errors. See [TWAP Oracle Pitfalls](./pattern-twap-oracle.md#common-pitfalls) for base issues.

| Pitfall | Impact | Solution |
|---------|--------|----------|
| **Inconsistent decimals** | Orders of magnitude error | Normalize each hop before combining |
| **Compounded rounding** | ~2× single-hop error | Use consistent rounding direction |
| **Token order confusion** | Inverted prices | Track `isToken0` separately for each pool |
| **Different TWAP windows** | Timing mismatch | Use same window for all hops |

## Operational Requirements

| Requirement | Why | How |
|-------------|-----|-----|
| **Pool whitelisting** | Dynamic discovery can be manipulated | Hardcode pool addresses, don't use `factory.getPool()` |
| **Liquidity thresholds** | Shallow pools are easily manipulated | Check `pool.liquidity() >= minThreshold` before using |
| **TWAP window consistency** | Timing mismatch causes errors | Use same window for all hops |
| **Intermediate token verification** | Wrong base asset = wrong price | Verify pool.token0/token1 match expected |

## Error Propagation

Multi-hop compounds errors:

```
Combined error ≈ error_hop1 + error_hop2

Example:
- Hop 1: 1% deviation
- Hop 2: 1% deviation
- Combined: ~2% deviation (can be higher during volatility)
```

**Mitigation:** Use tighter thresholds when multi-hop is involved.

## Limitations

**No Liquidity = No Price:**
If a token has no meaningful on-chain liquidity even versus major bases (WETH/WBTC), there is no honest DEX-derived price. In that case:
- Use off-chain oracle (Chainlink) if available
- Exclude asset from oracle-based flows
- Fail closed (revert rather than use bad price)

## Real-World Examples

- [Uniswap Router](https://docs.uniswap.org/contracts/v3/guides/swaps/multihop-swaps) — multi-hop swaps use same routing concept
- [1inch Pathfinder](https://docs.1inch.io/docs/aggregation-protocol/introduction) — complex routing for best prices

## Related Patterns

- [TWAP Oracle](./pattern-twap-oracle.md) — use TWAP for each hop
- [Multi-Source Validation](./pattern-multi-source-validation.md) — validate multi-hop against other sources
- [DEX Spot Price](./pattern-dex-spot-price.md) — single-hop spot alternative

## References

- [Uniswap V3 Multi-hop Swaps](https://docs.uniswap.org/contracts/v3/guides/swaps/multihop-swaps)
- [Price Oracle Design Patterns](https://blog.chain.link/defi-oracle-design-patterns/)

