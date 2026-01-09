# Oracle Reliability Requirements

> Core requirements that oracle integrations must satisfy for safe DeFi operations.

## Overview

These requirements define what "reliable" means for price oracle implementations. Patterns and risks in this category should reference these requirements to verify correctness.

---

## R1: Freshness

**Oracle data must be sufficiently recent for the use case.**

```
block.timestamp - lastUpdateTime <= maxStaleness
```

### What This Means
- Price data has a maximum acceptable age
- Different use cases have different freshness needs (lending vs. display)
- Stale data can enable arbitrage or cause incorrect liquidations

### Violations
- [Oracle Staleness Risk](./risk-oracle-staleness.md) — using outdated price data

### Solutions
- Check `updatedAt` timestamp from Chainlink
- Use on-chain TWAP with recent observations
- Implement staleness checks before using price

---

## R2: Accuracy

**Oracle price must reflect true market value within acceptable deviation.**

```
|oraclePrice - marketPrice| / marketPrice <= maxDeviation
```

### What This Means
- Price should be close to actual trading price
- Deviation threshold depends on asset volatility and use case
- Larger deviations create larger arbitrage opportunities

### Violations
- Large deviation thresholds (e.g., 1% for Chainlink)
- Infrequent updates during volatility
- Oracle lag during rapid price movements

### Solutions
- [Multi-Source Validation](./pattern-multi-source-validation.md) — cross-check multiple sources
- [TWAP Oracle](./pattern-twap-oracle.md) — smooth out short-term noise
- Circuit breakers during high deviation

---

## R3: Manipulation Resistance

**Oracle price must be economically infeasible to manipulate.**

```
cost_to_manipulate >> potential_profit_from_manipulation
```

### What This Means
- Flash loan attacks should not be profitable
- Single-block manipulation should not affect price
- Cost to move price must exceed extractable value

### Violations
- [Price Manipulation Risk](./risk-price-manipulation.md) — flash loan and sandwich attacks
- Using spot prices without protection
- Low liquidity pools for price discovery

### Solutions
- [TWAP Oracle](./pattern-twap-oracle.md) — time-weighted average resists single-block manipulation
- [Multi-Source Validation](./pattern-multi-source-validation.md) — require multiple sources to agree
- Liquidity requirements for price sources

---

## R4: Availability

**Oracle must provide price data when needed.**

```
oracle.getPrice() should not revert under normal conditions
```

### What This Means
- Price feed must be operational for protocol to function
- Fallback mechanisms for oracle downtime
- No single point of failure

### Violations
- [Oracle Centralization Risk](./risk-oracle-centralization.md) — single oracle dependency
- No fallback when primary oracle fails
- L2 sequencer downtime affecting oracle updates

### Solutions
- Multiple oracle sources with fallback logic
- [Multi-Source Validation](./pattern-multi-source-validation.md) — graceful degradation
- Chainlink L2 sequencer uptime feed

---

## Verification Checklist

When evaluating an oracle integration, verify:

| Requirement | Question to Ask |
|-------------|-----------------|
| R1 | How old can the price data be before it's rejected? |
| R2 | What's the maximum expected deviation from true price? |
| R3 | Can this price be manipulated within a single block/transaction? |
| R4 | What happens if the oracle is unavailable? |

---

## Requirement Interactions

Different patterns satisfy different combinations:

| Pattern | R1 | R2 | R3 | R4 |
|---------|----|----|----|----|
| [Chainlink Integration](./pattern-chainlink-integration.md) | ✅ | ⚠️ | ✅ | ⚠️ |
| [TWAP Oracle](./pattern-twap-oracle.md) | ✅ | ✅ | ✅ | ⚠️ |
| [Multi-Source Validation](./pattern-multi-source-validation.md) | ✅ | ✅ | ✅ | ✅ |
| [DEX Spot Price](./pattern-dex-spot-price.md) | ✅ | ✅ | ❌ | ✅ |

Legend: ✅ = satisfies, ⚠️ = partially satisfies, ❌ = does not satisfy

---

## Related Documents

### Patterns (Solutions)
- [Chainlink Integration](./pattern-chainlink-integration.md) — standard off-chain oracle
- [TWAP Oracle](./pattern-twap-oracle.md) — manipulation-resistant on-chain price
- [Multi-Source Validation](./pattern-multi-source-validation.md) — cross-check multiple sources
- [Multi-hop Price](./pattern-multihop-price.md) — derive price through intermediate asset
- [DEX Spot Price](./pattern-dex-spot-price.md) — current pool price
- [Historical Bounds](./pattern-historical-bounds.md) — sanity check against history

### Risks (Violations)
- [Oracle Staleness Risk](./risk-oracle-staleness.md) — violates R1
- [Price Manipulation Risk](./risk-price-manipulation.md) — violates R3
- [Oracle Frontrunning Risk](./risk-oracle-frontrunning.md) — violates R1, R2
- [Oracle Centralization Risk](./risk-oracle-centralization.md) — violates R4

