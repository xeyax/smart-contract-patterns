# Capped PnL Impact Pool Risk Accounting

> Compute perps pool value with capped trader PnL, pending fees, and separate price-impact pools before allowing actions that can extract liquidity.

## Metadata

| Property | Value |
|----------|-------|
| Category | perps |
| Tags | perps, pnl, impact-pool, risk, accounting |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A perpetuals market uses shared long and short liquidity pools
- Trader PnL can exceed a configurable fraction of pool value
- Price-impact accounting is accumulated in separate impact pools
- Actions should fail closed when pending PnL exceeds risk factors

## Avoid When

- The market settles every trade directly against an external orderbook
- Pool value does not include unrealized trader PnL
- Oracle freshness cannot be enforced on decrease or liquidation paths
- Socialized loss behavior is unacceptable or undocumented

## How It Works

Pool value is computed from inventory, pending fees, capped trader PnL, and impact-pool balances:

```solidity
poolValue =
    longTokenValue
  + shortTokenValue
  + pendingBorrowingFees
  + pendingFundingFees
  - cappedPositiveTraderPnl
  + cappedNegativeTraderPnl
  - positivePriceImpactPoolValue;

require(pendingPnl <= poolValue * maxPnlFactor / FACTOR, "pnl factor");
```

When a trader closes with positive PnL, the payout deducts from pool value. When a trade receives positive price impact, the impact-pool balance funds that improvement rather than treating it as free inventory.

A variant uses a PnL or fee pool as the first settlement boundary and then falls
through to insurance, bankruptcy handling, or socialized loss when capped pools
are insufficient. In that design, positive unrealized PnL may receive a lower
asset weight as exposure grows, and settlement should reject stale or divergent
oracle states before moving value.

## Key Points

- Cap positive and negative PnL according to market risk factors.
- Separate price-impact pool balances from ordinary token inventory.
- Gate withdrawals, decreases, or market actions when max-PnL factors are exceeded.
- Use fresh oracle prices for pool-value and PnL checks.
- Document that caps constrain pool exposure; they do not remove insolvency risk under stress.
- Define the order of loss absorption: PnL pool, fee pool, insurance or security module, bankruptcy, and any socialized loss.
- Test positive PnL caps, negative PnL caps, impact-pool depletion, and action gating.

## Source Evidence

- GMX Synthetics computes pool value from token inventory, pending fees, capped PnL, and impact pools, validates max-PnL factors, and tests capped-PnL decrease behavior.
- Drift caps PnL settlement through PnL and fee-pool limits, applies positive-PnL asset-weight discounts, and falls through liquidation, bankruptcy, and socialized-loss paths in `/private/tmp/defillama-source/drift-labs__protocol-v2/programs/drift/src/controller/pnl.rs` and `controller/liquidation.rs`.

## Related Patterns

- [ADL Reserve And Funding Risk Controls](./req-adl-reserve-and-funding-risk-controls.md)
- [Oracle Reliability Requirements](../oracles/req-oracle-reliability.md)
