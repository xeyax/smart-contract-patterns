# Bounded Rate Source Adapter

> Convert an external benchmark or savings rate into a lending rate only after applying freshness, bounds, spread, and fallback rules.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, interest-rate, adapter, benchmark, bounds, fallback |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Borrow or supply rates should follow an external benchmark
- The benchmark can be stale, paused, or temporarily unavailable
- Governance wants a fixed spread or capped transformation of the source rate
- Rate consumers need a standard interface even if sources differ

## Avoid When

- The external source has no on-chain freshness or monotonicity signal
- Fallback values could silently underprice risk
- The rate source can be manipulated by borrowers in the same market

## How It Works

Read the source, validate it, then bound the transformed output:

```solidity
function getBorrowRate() external view returns (uint256) {
    (uint256 sourceRate, uint256 updatedAt) = source.latestRate();
    require(block.timestamp - updatedAt <= maxStaleness, "stale rate");

    uint256 rate = sourceRate + spread;
    if (rate > maxRate) return maxRate;
    if (rate < minRate) return minRate;
    return rate;
}
```

Fallbacks must be explicit and conservative. A call that reverts because it ran out of gas, returned empty data, or hit an unexpected selector should not be treated as a valid zero or default rate.

## Key Points

- Validate source freshness before applying spreads or caps.
- Bound both the source rate and the transformed rate.
- Decide whether fallback is fail-closed or a conservative configured rate.
- Treat source replacement as a high-risk governance action.
- Test revert, empty return, stale return, extreme rate, and decimal mismatch paths.

## Source Evidence

- SparkLend Advanced adapts external savings and benchmark-style rates into lending rate models with bounded spreads and rate-model variants.

## Related Patterns

- [Kinked Utilization Rate Model](./pattern-kinked-utilization-rate-model.md)
- [Oracle Staleness Risk](../oracles/risk-oracle-staleness.md)
- [Unchecked External Return](../../ANTIPATTERNS.md#unchecked-external-return)
