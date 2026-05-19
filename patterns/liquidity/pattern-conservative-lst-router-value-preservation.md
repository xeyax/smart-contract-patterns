# Conservative LST Router Value Preservation

> Route swaps and liquidity changes across LST reserves only after syncing conservative underlying value and proving pool value does not decrease under the configured calculators.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | liquidity, lst, router, exchange-rate, value-preservation |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A pool routes between multiple liquid staking tokens
- Each reserve has a configured exchange-rate or SOL-value calculator
- The protocol can sync conservative reserve values before and after an operation
- User slippage and protocol value preservation must both hold

## Avoid When

- Calculator values are treated as market prices for lending or liquidation
- Reserve calculators are unbounded, stale, or not allowlisted
- Operations cannot afford pre/post value syncs
- Hooks or callbacks can change reserve balances during measurement

## How It Works

Before a swap or liquidity change, sync the conservative value of every affected reserve. Execute the operation, sync again, and require aggregate value preservation:

```rust
let start_value = sync_total_sol_value(reserves)?;
execute_swap_or_liquidity_change()?;
let end_value = sync_total_sol_value(reserves)?;

require!(end_value >= start_value, PoolValueDecreased);
require!(user_out >= min_out, Slippage);
```

Calculator outputs should use conservative rounding and bounded conversion rules. The invariant protects accounting under those calculators; it does not prove the LST can be sold at that value in the market.

## Key Points

- Sync every affected reserve before and after the operation.
- Use allowlisted calculators with bounded/min-value conversion semantics.
- Enforce user slippage in addition to protocol value preservation.
- Reject operations that reduce total underlying value under the configured accounting model.
- Cross-check exchange-rate risk when the output is used as collateral or NAV.
- Test value-increase, value-decrease, stale calculator, and slippage-failure cases.

## Source Evidence

- Sanctum's multi-LST controller syncs reserve SOL value through configured calculators before and after swaps or liquidity changes, enforces user slippage, and rejects operations that reduce total pool SOL value.

## Related Patterns

- [Exchange-Rate Valuation Risk](../oracles/risk-exchange-rate-valuation.md)
- [Conservative AMM LP Collateral Oracle](../oracles/pattern-conservative-amm-lp-collateral-oracle.md)
