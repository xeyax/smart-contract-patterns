# Dynamic Premium

> Entry/exit fee that varies based on oracle volatility, providing adaptive protection against oracle arbitrage during high-risk periods.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, fee, premium, oracle, dynamic, adaptive |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Vault has varying risk levels over time
- Fixed premium would be too high during normal conditions
- Assets have periods of high and low volatility
- Want lower fees during stable market conditions

## Avoid When

- Need predictable, fixed fees for UX
- Gas cost of premium calculation is prohibitive
- Vault risk profile is stable
- Simple fixed premium is sufficient
- Historical price data not available

## Trade-offs

**Pros:**
- Adaptive protection: fee matches actual risk
- Lower cost for users during stable periods
- Fair: high volatility = high oracle risk = higher fee
- More precise than fixed premium

**Cons:**
- Complex fee calculation
- Harder for users to predict cost
- Requires reliable volatility metrics
- More surface area for bugs

## How It Works

Premium calculated as function of volatility:

```
premium = basePremium + volatilityComponent
```

Where:
- **basePremium** — minimum fee (covers oracle's normal deviation threshold)
- **volatilityComponent** — increases during high price volatility

**Why volatility matters:** High volatility = oracle more likely to be stale relative to real price = higher arbitrage risk.

## Requirements Satisfied

This pattern satisfies [Vault Fairness Requirements](./req-vault-fairness.md):
- **R1: No Value Extraction** — premium ≥ potential arbitrage profit

## Implementation

Premium increases during high price volatility:

```solidity
contract VolatilityBasedPremiumVault {
    uint256 public basePremiumBps;
    uint256 public maxVolatilityPremiumBps;

    // Store recent prices for volatility calculation
    uint256[] public priceHistory;
    uint256 public historyWindow;  // e.g., 24 data points

    function calculatePremium() public view returns (uint256) {
        uint256 volatility = _calculateVolatility();

        // Scale premium with volatility
        // volatility in bps (e.g., 500 = 5% daily volatility)
        uint256 volPremium = volatility * maxVolatilityPremiumBps / 1000;

        return basePremiumBps + Math.min(volPremium, maxVolatilityPremiumBps);
    }

    function _calculateVolatility() internal view returns (uint256) {
        if (priceHistory.length < 2) return 0;

        uint256 sumSquaredReturns = 0;
        for (uint i = 1; i < priceHistory.length; i++) {
            uint256 returnBps;
            if (priceHistory[i] > priceHistory[i-1]) {
                returnBps = (priceHistory[i] - priceHistory[i-1]) * BPS / priceHistory[i-1];
            } else {
                returnBps = (priceHistory[i-1] - priceHistory[i]) * BPS / priceHistory[i-1];
            }
            sumSquaredReturns += returnBps * returnBps;
        }

        // Simple volatility estimate (not annualized)
        return Math.sqrt(sumSquaredReturns / (priceHistory.length - 1));
    }

    function updatePriceHistory() external {
        uint256 currentPrice = _getOraclePrice();

        if (priceHistory.length >= historyWindow) {
            // Shift array (gas-intensive, consider circular buffer)
            for (uint i = 0; i < priceHistory.length - 1; i++) {
                priceHistory[i] = priceHistory[i + 1];
            }
            priceHistory[priceHistory.length - 1] = currentPrice;
        } else {
            priceHistory.push(currentPrice);
        }
    }
}
```

## Premium Calculation Examples

| Daily Volatility | Base | Vol Premium | Total |
|------------------|------|-------------|-------|
| 1% (low) | 0.25% | 0.2% | 0.45% |
| 3% (normal) | 0.25% | 0.6% | 0.85% |
| 5% (high) | 0.25% | 1% | 1.25% |
| 10%+ (extreme) | 0.25% | 2% (capped) | 2.25% |

## Variations

### Time-Decaying Premium

Higher premium right after large price moves:

```solidity
uint256 public lastLargeMoveTime;
uint256 public decayPeriod;  // e.g., 1 hour

function calculatePremium() public view returns (uint256) {
    uint256 timeSinceMove = block.timestamp - lastLargeMoveTime;

    if (timeSinceMove >= decayPeriod) {
        return basePremiumBps;
    }

    // Linear decay from maxPremium to basePremium
    uint256 decayFactor = timeSinceMove * BPS / decayPeriod;
    uint256 extraPremium = maxExtraPremiumBps * (BPS - decayFactor) / BPS;

    return basePremiumBps + extraPremium;
}
```

## Gas Considerations

- Drift calculation: O(n) where n = number of assets
- Volatility calculation: O(m) where m = history window size
- Consider:
  - Caching premium with periodic updates
  - Off-chain calculation with on-chain verification
  - Simplified proxy metrics

## Related Patterns

- [Premium Buffer](./pattern-premium-buffer.md) — fixed premium (simpler version)
- [Oracle Arbitrage Risk](./risk-oracle-arbitrage.md) — the problem this solves
- [Circuit Breaker](./pattern-circuit-breaker.md) — complementary protection

## References

- [Set Protocol Premium Mechanism](https://docs.tokensets.com/developers/contracts/protocol/modules/nav-issuance-module)
- [Balancer Dynamic Fees](https://docs.balancer.fi/concepts/pools/dynamic-swap-fees.html)
