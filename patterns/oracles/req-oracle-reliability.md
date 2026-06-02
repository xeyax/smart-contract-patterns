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
- Wrapper feeds must expose the oldest underlying source timestamp, not a synthetic current timestamp
- Composite feeds must propagate the oldest or limiting timestamp from every leg used in the price path, including multiplication chains.
- Chainlink-compatible consumers must not discard the wrapper-provided timestamp and then rely only on positivity or decimal normalization.
- Bridged rate providers must expose source-chain freshness separately from destination-chain relay execution time
- Off-chain state reports over block ranges must be finalized and contiguous: each accepted range starts at the previous range's end plus one, ends after it starts, and is older than the configured finalization buffer.
- Oracle node graphs must normalize leaf price and timestamp data and make
  staleness checks explicit at the consuming node, not implicit in a leaf that
  may use unsafe reads.
- Execution-time TWAP guards must prove the observation window is actually
  available for every pool or hop used in the path.

### Violations
- [Oracle Staleness Risk](./risk-oracle-staleness.md) — using outdated price data

### Solutions
- Check `updatedAt` timestamp from Chainlink
- Use on-chain TWAP with recent observations
- Implement staleness checks before using price
- Reject `latestAnswer()`-only integrations for value-bearing operations
- For composite feeds, carry the minimum source timestamp through chained calculations instead of stamping derived prices with the refresh time.

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
- Accepted state updates should be bounded by both value delta and update cadence
- Lending collateral oracles should preserve enough liquidation buffer that an allowed oracle jump cannot instantly push healthy accounts below the intended liquidation threshold.
- Perps or portfolio-margin systems should define action-specific validity for funding, settlement, liquidation, trigger, margin, and AMM-fill paths instead of relying on one global fresh/stale flag.
- Confidence intervals and exponent normalization should be checked before converting an oracle report into the protocol's fixed precision.
- Oracle metadata updates should reject missing mappings, duplicate token mappings, and unsupported source counts before a price path can be refreshed.
- Circuit-breaker nodes should encode freshness, deviation, and fallback policy
  as machine-checkable graph behavior, not as off-chain routing convention.

### Violations
- Large deviation thresholds (e.g., 1% for Chainlink)
- Infrequent updates during volatility
- Oracle lag during rapid price movements

### Solutions
- [Multi-Source Validation](./pattern-multi-source-validation.md) — cross-check multiple sources
- [TWAP Oracle](./pattern-twap-oracle.md) — smooth out short-term noise
- [Historical Bounds](./pattern-historical-bounds.md) — reject excessive, stale, non-monotonic, or future-dated accepted-state updates
- Circuit breakers during high deviation
- Listing-time inequalities that compare maximum oracle jumps against LLTV, liquidation incentive, and collateral liquidity

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
- For off-chain lookup or pull-oracle feeds, stale data should revert with enough
  machine-readable query data for keepers or clients to refresh the source.
- For router slippage guards, unavailable observation cardinality or missing
  path history should fail closed instead of silently falling back to spot.

---

## Source Evidence

- Kamino Scope propagates source timestamps through multiplication-chain composites, validates mapping metadata before refresh, and distinguishes most-recent agreement from capped most-recent agreement in `/private/tmp/defillama-source/Kamino-Finance_scope/programs/scope/src/oracles/multiplication_chain.rs`, `handlers/handler_update_mapping_and_metadata.rs`, `handlers/handler_refresh_prices.rs`, `oracles/most_recent_of.rs`, and `oracles/capped_most_recent_of.rs`.
- Synthetix V3 oracle-manager composes leaf nodes with staleness and deviation
  circuit-breaker nodes, while its Pyth leaf uses unsafe reads only inside a
  graph that can add staleness/off-chain lookup behavior in
  `/private/tmp/defillama-source/synthetixio__synthetix-v3/protocol/oracle-manager/contracts/nodes/pyth/PythNode.sol:17-48`,
  `/private/tmp/defillama-source/synthetixio__synthetix-v3/protocol/oracle-manager/contracts/nodes/StalenessCircuitBreakerNode.sol:14-66`,
  `/private/tmp/defillama-source/synthetixio__synthetix-v3/protocol/oracle-manager/contracts/nodes/PriceDeviationCircuitBreakerNode.sol:17-67`,
  and `/private/tmp/defillama-source/synthetixio__synthetix-v3/protocol/oracle-manager/contracts/nodes/pyth/PythOffchainLookupNode.sol:18-68`.
- Uniswap swap-router TWAP slippage checks reject paths whose observation data is
  unavailable or insufficient in `/private/tmp/defillama-source/Uniswap__swap-router-contracts/contracts/base/OracleSlippage.sol:17`
  and `/private/tmp/defillama-source/Uniswap__swap-router-contracts/test/OracleSlippage.spec.ts:339`.
- Inverse FiRM's pessimistic feed wrappers propagate the older underlying
  `updatedAt` timestamp in `/private/tmp/defillama-source/InverseFinance__FiRM/src/feeds/PessimisticFeed.sol`, while its main oracle illustrates why consumers still need to check the timestamp returned by `latestRoundData` instead of reading only the price in `/private/tmp/defillama-source/InverseFinance__FiRM/src/Oracle.sol`.

---

## Verification Checklist

When evaluating an oracle integration, verify:

| Requirement | Question to Ask |
|-------------|-----------------|
| R1 | How old can the price data be before it's rejected? |
| R2 | What's the maximum expected deviation from true price? |
| R3 | Can this price be manipulated within a single block/transaction? |
| R4 | What happens if the oracle is unavailable? |
| Wrappers | Does the feed preserve source freshness and round semantics? |
| Bridged Rates | Is the source update timestamp checked separately from the message receive timestamp? |
| Report Ranges | Are off-chain source ranges finalized, contiguous, and non-sparse? |
| Action Scope | Which price-validity flags are required for each value-bearing action? |
| Confidence | Are confidence ratios, exponent ranges, and feed ids validated before conversion? |
| Market Dependency | If the core delegates oracle choice to market creators, are scale, no-revert, magnitude, and unsafe-jump assumptions documented? |
| Composite Metadata | Are source mappings unique and complete before a composite price path can refresh? |
| Node Graphs | Are leaf values normalized and guarded by explicit staleness/deviation/fallback nodes before value-bearing use? |
| Execution TWAP | Does every route hop have enough observation history before the path is accepted? |
| Wrapper Consumption | Does the consumer use the wrapper's returned timestamp and round metadata, not only the answer value? |

---

## Requirement Interactions

Different patterns satisfy different combinations:

| Pattern | R1 | R2 | R3 | R4 |
|---------|----|----|----|----|
| [Chainlink Integration](./pattern-chainlink-integration.md) | ✅ | ⚠️ | ✅ | ⚠️ |
| [TWAP Oracle](./pattern-twap-oracle.md) | ✅ | ✅ | ✅ | ⚠️ |
| [Multi-Source Validation](./pattern-multi-source-validation.md) | ✅ | ✅ | ✅ | ✅ |
| [Threshold Reporter Consensus](./pattern-threshold-reporter-consensus.md) | ⚠️ | ⚠️ | ⚠️ | ⚠️ |
| [Peg Ratio Monitor](./pattern-peg-ratio-monitor.md) | ⚠️ | ⚠️ | ⚠️ | ❌ |
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
- [Threshold Reporter Consensus](./pattern-threshold-reporter-consensus.md) — quorum-gated accepted state
- [Peg Ratio Monitor](./pattern-peg-ratio-monitor.md) — monitor market/fair-value divergence
- [User Opt-In Pending Oracle Registry](./pattern-user-opt-in-pending-oracle-registry.md) — staged oracle replacement with consumer opt-in caveats

### Risks (Violations)
- [Oracle Staleness Risk](./risk-oracle-staleness.md) — violates R1
- [Price Manipulation Risk](./risk-price-manipulation.md) — violates R3
- [Oracle Frontrunning Risk](./risk-oracle-frontrunning.md) — violates R1, R2
- [Oracle Centralization Risk](./risk-oracle-centralization.md) — violates R4
- [Exchange-Rate Valuation Risk](./risk-exchange-rate-valuation.md) — affects R2, R3
