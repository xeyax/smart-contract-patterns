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

## Trade-offs

**Pros:**
- PnL caps stop one oracle move or whale position from claiming the entire pool as payable profit.
- Separate impact pools prevent price-impact rebates from being mistaken for free token inventory.
- Fail-closed gating on max-PnL factors protects LPs from withdrawal runs during pending-PnL spikes.
- An explicit loss-absorption order (PnL pool, fee pool, insurance, bankruptcy, socialization) makes stress behavior auditable in advance.

**Cons:**
- The pool-value formula mixes inventory, pending fees, capped PnL, and impact pools — a large, error-prone accounting and audit surface.
- Winning traders can be haircut or delayed by caps, creating UX and disclosure burdens.
- Caps bound exposure but do not remove insolvency risk; a socialized-loss path is still required under stress.
- Gated withdrawals and decreases can lock users out exactly when they most want to exit.
- Every check needs fresh oracle prices, so oracle outages stall liquidations, decreases, and settlement.

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

Another variant caps payoff per position against a custody or pool-level maximum
profit ratio. The cap is applied before pool AUM and payout checks so one
position cannot treat the entire reserve as claimable PnL.

## Key Points

- Cap positive and negative PnL according to market risk factors.
- Separate price-impact pool balances from ordinary token inventory.
- Gate withdrawals, decreases, or market actions when max-PnL factors are exceeded.
- Use fresh oracle prices for pool-value and PnL checks.
- Document that caps constrain pool exposure; they do not remove insolvency risk under stress.
- Define the order of loss absorption: PnL pool, fee pool, insurance or security module, bankruptcy, and any socialized loss.
- Apply per-position payoff caps before reserve or AUM checks when the protocol promises a maximum user profit ratio.
- Test positive PnL caps, negative PnL caps, impact-pool depletion, and action gating.

## Source Evidence

- GMX Synthetics computes pool value from token inventory, pending fees, capped PnL, and impact pools, validates max-PnL factors, and tests capped-PnL decrease behavior.
- Drift caps PnL settlement through PnL and fee-pool limits, applies positive-PnL asset-weight discounts, and falls through liquidation, bankruptcy, and socialized-loss paths in [`programs/drift/src/controller/pnl.rs`](https://github.com/drift-labs/protocol-v2/blob/0ae3e3b1db782a6765c3525b3dec38ad4d9d3a62/programs/drift/src/controller/pnl.rs) and `controller/liquidation.rs`.
- Solana Labs Perpetuals caps per-position user profit against custody limits before pool AUM and payout checks, with tests for maximum user profit in [`programs/perpetuals/src/state/custody.rs`](https://github.com/solana-labs/perpetuals/blob/ebfb4972ea5d1cde8580a7e8c7b9dbd1fdb2b002/programs/perpetuals/src/state/custody.rs), `programs/perpetuals/src/state/pool.rs`, and `programs/perpetuals/tests/native/tests_suite/position/max_user_profit.rs`.

## Related Patterns

- [ADL Reserve And Funding Risk Controls](./req-adl-reserve-and-funding-risk-controls.md)
- [Oracle Reliability Requirements](../oracles/req-oracle-reliability.md)
