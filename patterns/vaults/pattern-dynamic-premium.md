# Dynamic Premium

> Entry/exit fee that varies based on vault conditions (drift from target, oracle volatility), providing adaptive protection against oracle arbitrage.

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
- Want fair pricing: higher risk → higher fee
- Vault tracks target weights that can drift

## Avoid When

- Need predictable, fixed fees for UX
- Gas cost of premium calculation is prohibitive
- Vault risk profile is stable
- Simple fixed premium is sufficient

## Trade-offs

**Pros:**
- Adaptive protection: fee matches actual risk
- Lower cost for users during low-risk periods
- Incentivizes deposits when vault is balanced
- More precise than fixed premium

**Cons:**
- Complex fee calculation
- Harder for users to predict cost
- Requires reliable risk metrics (drift, volatility)
- More surface area for bugs

## How It Works

Premium calculated as function of risk factors:

```
premium = basePremium + driftComponent + volatilityComponent
```

Where:
- **basePremium** — minimum fee (covers oracle's normal deviation)
- **driftComponent** — increases when vault is off-target
- **volatilityComponent** — increases during high price volatility

## Requirements Satisfied

This pattern satisfies [Vault Fairness Requirements](./req-vault-fairness.md):
- **R1: No Value Extraction** — premium ≥ potential arbitrage profit

## Implementation

### Drift-Based Premium

Premium increases when vault composition differs from target:

```solidity
contract DriftBasedPremiumVault {
    uint256 public basePremiumBps;       // e.g., 25 = 0.25%
    uint256 public maxDriftPremiumBps;   // e.g., 200 = 2%
    uint256 constant BPS = 10000;

    function calculatePremium() public view returns (uint256) {
        uint256 drift = _calculateDrift();

        // Linear scaling: drift 0% → base, drift 10% → base + maxDrift
        uint256 driftPremium = drift * maxDriftPremiumBps / 1000;  // 1000 = 10%

        return basePremiumBps + Math.min(driftPremium, maxDriftPremiumBps);
    }

    function _calculateDrift() internal view returns (uint256) {
        uint256 totalDrift = 0;

        for (uint i = 0; i < assets.length; i++) {
            uint256 currentWeight = _getCurrentWeight(assets[i]);
            uint256 targetWeight = _getTargetWeight(assets[i]);

            // Sum of absolute deviations
            if (currentWeight > targetWeight) {
                totalDrift += currentWeight - targetWeight;
            } else {
                totalDrift += targetWeight - currentWeight;
            }
        }

        return totalDrift / 2;  // Divide by 2 since deviations sum to 2x
    }

    function deposit(uint256[] calldata amounts) external returns (uint256 shares) {
        uint256 premium = calculatePremium();
        uint256 nav = _calculateNav();
        uint256 depositValue = _calculateDepositValue(amounts);

        // Apply premium
        uint256 effectiveValue = depositValue * (BPS - premium) / BPS;
        shares = effectiveValue * totalShares / nav;

        _acceptDeposit(amounts);
        _mintShares(msg.sender, shares);
    }

    // --- Abstract functions ---
    function _getCurrentWeight(address asset) internal view returns (uint256);
    function _getTargetWeight(address asset) internal view returns (uint256);
    function _calculateNav() internal view returns (uint256);
    function _calculateDepositValue(uint256[] calldata amounts) internal view returns (uint256);
}
```

### Volatility-Based Premium

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

### Combined Premium

```solidity
function calculatePremium() public view returns (uint256) {
    uint256 drift = _calculateDrift();
    uint256 volatility = _calculateVolatility();

    uint256 driftPremium = drift * maxDriftPremiumBps / 1000;
    uint256 volPremium = volatility * maxVolatilityPremiumBps / 1000;

    uint256 totalPremium = basePremiumBps + driftPremium + volPremium;

    return Math.min(totalPremium, maxTotalPremiumBps);
}
```

## Premium Calculation Examples

### Drift-Based

| Drift from Target | Base | Drift Premium | Total |
|-------------------|------|---------------|-------|
| 0% (perfectly balanced) | 0.25% | 0% | 0.25% |
| 2% | 0.25% | 0.4% | 0.65% |
| 5% | 0.25% | 1% | 1.25% |
| 10%+ | 0.25% | 2% (capped) | 2.25% |

### Volatility-Based

| Daily Volatility | Base | Vol Premium | Total |
|------------------|------|-------------|-------|
| 1% (low) | 0.25% | 0.2% | 0.45% |
| 3% (normal) | 0.25% | 0.6% | 0.85% |
| 5% (high) | 0.25% | 1% | 1.25% |
| 10%+ (extreme) | 0.25% | 2% (capped) | 2.25% |

## Variations

### Asymmetric Premium (Rebalancing Incentive)

Lower fee for deposits that help rebalance:

```solidity
function calculateDepositPremium(uint256[] calldata amounts) public view returns (uint256) {
    uint256 basePremium = calculatePremium();

    // Check if deposit improves balance
    bool improvesBalance = _depositImprovesBalance(amounts);

    if (improvesBalance) {
        // Discount for helpful deposits
        return basePremium * 75 / 100;  // 25% discount
    }

    return basePremium;
}
```

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
