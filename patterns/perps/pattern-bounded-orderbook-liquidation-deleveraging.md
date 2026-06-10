# Bounded Orderbook Liquidation Deleveraging

> Cap per-block orderbook liquidation attempts and fall back to deterministic deleveraging when fills cannot safely absorb risk.

## Metadata

| Property | Value |
|----------|-------|
| Category | perps |
| Tags | perps, liquidation, orderbook, deleveraging, insurance |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Perpetual positions are liquidated through an orderbook or matching engine
- Liquidation size and price must consider bankruptcy, fillability, and insurance loss
- A liquidation attempt can fail or be insufficient in a volatile market
- The protocol needs a bounded fallback that reduces systemic risk

## Avoid When

- Liquidation is direct AMM inventory transfer with no orderbook matching
- Insurance, ADL, or deleveraging semantics are intentionally off-chain
- The protocol cannot define deterministic ordering for forced deleveraging

## Trade-offs

**Pros:**
- Prevents liquidation loops from consuming unbounded block resources
- Makes insurance-fund loss checks explicit before fills
- Provides a fallback when orderbook liquidity is insufficient

**Cons:**
- Deleveraging can socialize losses or reduce profitable counterparty positions
- Parameter calibration affects both solvency and market fairness
- Deterministic fallback logic is complex to test

## How It Works

The protocol attempts a bounded number of orderbook liquidations per block.
Each liquidation computes bankruptcy price, fillable price, maximum position
size, and insurance-fund loss. If orderbook liquidation cannot sufficiently
resolve a position, a deleveraging pass selects offsetting positions under
bounded iteration.

```go
func EndBlockLiquidations(ctx Context) {
    for attempts := 0; attempts < MaxLiquidationAttemptsPerBlock; attempts++ {
        subaccount := nextLiquidatableSubaccount(ctx)
        if subaccount == nil {
            break
        }

        if !tryOrderbookLiquidation(ctx, subaccount) {
            maybeDeleverageSubaccount(ctx, subaccount)
        }
    }
}
```

## Implementation

- Cap liquidation attempts and deleveraging iterations per block.
- Compute bankruptcy and fillable prices from current margin state.
- Bound liquidation order size, notional, and insurance-fund loss.
- Gate withdrawals and transfers after negative total net collateral.
- Test empty orderbook, partial fills, insurance exhaustion, dust positions, and deleveraging iteration caps.

## Source Evidence

- dYdX v4 caps orderbook liquidation attempts in [`protocol/x/clob/keeper/liquidations.go`](https://github.com/dydxprotocol/v4-chain/blob/5ee9766351ef864856a309a971b13fdd98cae2c5/protocol/x/clob/keeper/liquidations.go) through `LiquidateSubaccountsAgainstOrderbook`.
- dYdX computes liquidation order, bankruptcy price, fillable price, and insurance-fund delta in the same file.
- dYdX bounds liquidation position size, notional, insurance loss, and min/max notional in `liquidations.go`.
- dYdX deleveraging logic lives in `protocol/x/clob/keeper/deleveraging.go`, including eligibility, offsetting positions, and iteration caps.
- dYdX gates withdrawals and transfers after negative total net collateral in `protocol/x/subaccounts/keeper/subaccount.go`.

## Real-World Examples

- dYdX v4 combines bounded orderbook liquidations with deleveraging fallback.

## Related Patterns

- [Perps ADL, Reserve, And Funding Risk Controls](./req-adl-reserve-and-funding-risk-controls.md)
- [Capped PnL Impact Pool Risk Accounting](./pattern-capped-pnl-impact-pool-risk-accounting.md)
- [Toxic Liquidation Spiral](../../ANTIPATTERNS.md#toxic-liquidation-spiral)

## References

- dYdX v4 CLOB liquidation and deleveraging source.
