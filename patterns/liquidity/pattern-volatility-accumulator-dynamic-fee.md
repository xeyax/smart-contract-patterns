# Volatility-Accumulator Dynamic Fee

> Increase AMM swap fees from a decaying accumulator of recent price movement and trade clustering instead of only inventory imbalance.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, dynamic-fee, volatility, swap, solana |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A pool wants fees to rise during rapid price movement or clustered trading
- Off-peg or inventory-imbalance fees do not capture the main risk
- The fee state can decay over time when volatility subsides
- Quotes and execution can share the same fee calculation

## Avoid When

- Pool pricing does not expose a stable volatility input
- Governance cannot bound fee parameters tightly
- Integrators cannot simulate current dynamic fees before trading
- The fee can jump after a user signs a transaction without slippage protection

## How It Works

Track a volatility reference and accumulator updated during swaps:

```solidity
function updateFeeState(uint256 currentPrice) internal {
    if (block.timestamp > lastUpdate + decayWindow) {
        volatilityAccumulator = _decay(volatilityAccumulator);
    }

    uint256 priceMove = _distance(currentPrice, lastReferencePrice);
    if (priceMove > filterPeriodThreshold) {
        volatilityAccumulator += priceMove;
        lastReferencePrice = currentPrice;
    }
}

function dynamicFeeBps() public view returns (uint256) {
    return baseFeeBps + min(maxVolatilityFeeBps, volatilityAccumulator * feeFactor);
}
```

The accumulator should be capped and decay so the pool does not stay permanently expensive after temporary volatility.

## Key Points

- Bound base fee, max dynamic fee, accumulator growth, and decay windows.
- Use identical fee math for quote and execution.
- Require user slippage limits because fee state can change between quote and execution.
- Test filter-period, decay, cap, and repeated-swap behavior.
- Keep this distinct from off-peg dynamic fees that price inventory imbalance.
- Monitor parameter changes as economic risk settings.

## Source Evidence

- Loopscale's cloned DAMM v2 source identifies as Meteora constant-product AMM code and includes volatility accumulator fee state, decay behavior, and dynamic-fee tests.

## Related Patterns

- [Off-Peg Dynamic Fee](./pattern-offpeg-dynamic-fee.md)
- [Constant-Product AMM Invariants](./req-constant-product-amm-invariants.md)
- [Missing Slippage Protection](../../ANTIPATTERNS.md#missing-slippage-protection)
