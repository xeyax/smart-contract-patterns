# Circuit Breaker

> Pause deposits/withdrawals when oracle price deviates significantly from a reference price, closing the attack window during suspicious conditions.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults, security |
| Tags | vault, oracle, circuit-breaker, safety, pause, twap |
| Complexity | Low |
| Gas Efficiency | High |
| Audit Risk | Low |

## Use When

- Vault relies on oracle for NAV calculation
- Assets are volatile or oracle is known to have latency
- Safety is prioritized over guaranteed liquidity
- Want a fallback protection layer on top of other mitigations

## Avoid When

- Users need guaranteed deposit/withdrawal availability
- Oracle deviation is expected (e.g., during high volatility)
- No reliable reference price (TWAP, secondary oracle) available
- Vault is time-sensitive (options, liquidations)

## Trade-offs

**Pros:**
- Simple to implement
- Zero cost when not triggered
- Completely closes attack window during deviation
- Works as safety net alongside other protections

**Cons:**
- May block legitimate deposits during volatile markets
- Requires reliable reference price source
- Can be exploited to DOS the vault (trigger circuit breaker intentionally)
- Users may be stuck unable to exit during market stress

## How It Works

Compare primary oracle price against a reference:
- **TWAP** — time-weighted average from DEX
- **Secondary oracle** — different price feed
- **Historical bounds** — min/max over recent period

If deviation exceeds threshold, reject the operation:

```
deviation = |oraclePrice - referencePrice| / referencePrice

if deviation > threshold:
    revert("Circuit breaker: oracle deviation too high")
```

## Requirements Satisfied

This pattern satisfies [Vault Fairness Requirements](./req-vault-fairness.md):
- **R4: No Timing Advantage** — attack window closed during deviation

## Implementation

```solidity
contract CircuitBreakerVault {
    uint256 public maxDeviationBps;  // e.g., 200 = 2%
    uint256 constant BPS = 10000;

    modifier circuitBreakerCheck() {
        uint256 oraclePrice = _getOraclePrice();
        uint256 referencePrice = _getReferencePrice();

        uint256 deviation = _calculateDeviation(oraclePrice, referencePrice);
        require(deviation <= maxDeviationBps, "Circuit breaker: deviation too high");
        _;
    }

    function deposit(uint256 assets) external circuitBreakerCheck returns (uint256 shares) {
        // ... deposit logic
    }

    function withdraw(uint256 sharesToBurn) external circuitBreakerCheck returns (uint256 assets) {
        // ... withdraw logic
    }

    function _calculateDeviation(uint256 a, uint256 b) internal pure returns (uint256) {
        if (a > b) {
            return (a - b) * BPS / b;
        } else {
            return (b - a) * BPS / a;
        }
    }

    // --- Abstract functions ---
    function _getOraclePrice() internal view returns (uint256);
    function _getReferencePrice() internal view returns (uint256);  // TWAP, secondary oracle, etc.
}
```

### Multi-Asset Variant

For multi-asset vaults, check each asset's oracle:

```solidity
modifier circuitBreakerCheckAll() {
    for (uint i = 0; i < assets.length; i++) {
        uint256 oraclePrice = _getOraclePrice(assets[i]);
        uint256 referencePrice = _getReferencePrice(assets[i]);
        uint256 deviation = _calculateDeviation(oraclePrice, referencePrice);

        require(deviation <= maxDeviationBps, "Circuit breaker triggered");
    }
    _;
}
```

## Reference Price Sources

| Source | Pros | Cons |
|--------|------|------|
| **Uniswap TWAP** | On-chain, manipulation-resistant | Requires liquidity, gas cost |
| **Secondary Chainlink feed** | Independent source | May have same issues |
| **Historical bounds** | Simple | Doesn't detect slow drift |
| **Off-chain oracle** | Fast updates | Centralization risk |

## Calibration

| Asset Type | Suggested Threshold | Rationale |
|------------|---------------------|-----------|
| Stablecoins | 0.5-1% | Should be very stable |
| Major tokens (ETH, BTC) | 2-3% | Normal volatility |
| Altcoins | 5-10% | Higher volatility expected |

**Considerations:**
- Too tight: frequent false positives, bad UX
- Too loose: attacks possible within threshold
- Should be wider than oracle's own deviation threshold

## Variations

### Time-Based Cooldown

After circuit breaker triggers, require cooldown before re-enabling:

```solidity
uint256 public lastTriggerTime;
uint256 public cooldownPeriod;

modifier circuitBreakerCheck() {
    require(block.timestamp > lastTriggerTime + cooldownPeriod, "Cooldown active");

    uint256 deviation = _calculateDeviation(...);
    if (deviation > maxDeviationBps) {
        lastTriggerTime = block.timestamp;
        revert("Circuit breaker triggered");
    }
    _;
}
```

### Graduated Response

Different thresholds for different actions:

```solidity
uint256 public depositThreshold;   // e.g., 2%
uint256 public withdrawThreshold;  // e.g., 5% (more permissive for exits)
```

### Emergency Override

Allow governance to temporarily disable:

```solidity
bool public circuitBreakerEnabled = true;

function setCircuitBreakerEnabled(bool enabled) external onlyGovernance {
    circuitBreakerEnabled = enabled;
}
```

## Attack Vector: Intentional Triggering

**Risk:** Attacker manipulates reference price (e.g., TWAP via DEX) to trigger circuit breaker and DOS the vault.

**Mitigations:**
- Use manipulation-resistant TWAP (long window, high liquidity)
- Multiple reference sources
- Governance override for emergencies
- Time-limited pause (auto-resume after N blocks)

## Real-World Examples

- [Chainlink Circuit Breakers](https://blog.chain.link/circuit-breakers-and-client-diversity-within-the-chainlink-network/) — price feed safety mechanisms
- [Aave Price Oracle](https://docs.aave.com/developers/core-contracts/aaveoracle) — price sanity checks
- [MakerDAO OSM](https://docs.makerdao.com/smart-contract-modules/oracle-module/oracle-security-module-osm-detailed-documentation) — delayed price updates with bounds

## Related Patterns

- [Oracle Arbitrage Risk](./risk-oracle-arbitrage.md) — the problem this helps mitigate
- [Premium Buffer](./pattern-premium-buffer.md) — alternative/complementary protection
- [Async Deposit/Withdrawal](./pattern-async-deposit.md) — alternative protection

## References

- [Chainlink Data Feeds](https://docs.chain.link/data-feeds)
- [Uniswap V3 TWAP Oracle](https://docs.uniswap.org/concepts/protocol/oracle)
