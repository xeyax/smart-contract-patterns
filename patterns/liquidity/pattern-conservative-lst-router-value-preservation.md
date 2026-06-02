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

Pools with withheld-yield or protocol-fee buckets should compare user operations against LP-due value, not raw reserve value. Withheld yield can smooth NAV and fund protocol fees, but it is not immediately owed to LP shares until the release logic moves it into the LP-due bucket.

Calculator replacement is also part of the value-preservation boundary. A new calculator should be allowlisted, validate executable identity and account suffixes, and resync the affected reserve before user operations can rely on the new conversion range.

## Key Points

- Sync every affected reserve before and after the operation.
- Use allowlisted calculators with bounded/min-value conversion semantics.
- Enforce user slippage in addition to protocol value preservation.
- Reject operations that reduce total underlying value under the configured accounting model.
- Cross-check exchange-rate risk when the output is used as collateral or NAV.
- When the pool has withheld-yield or protocol-fee buckets, compare LP value against LP-due assets rather than raw pool assets.
- Changing a calculator should validate executable identity and immediately resync the affected reserve before it prices user operations.
- Test value-increase, value-decrease, stale calculator, and slippage-failure cases.

## Source Evidence

- Sanctum's multi-LST controller syncs reserve SOL value through configured calculators before and after swaps or liquidity changes, enforces user slippage, and rejects operations that reduce total pool SOL value.
- Sanctum INF separates total pool SOL value from LP-due value by excluding withheld yield and protocol fees in `/private/tmp/defillama-source/igneous-labs_inf-1.5/controller/core/src/accounts/pool_state/v2.rs`, `controller/core/src/typedefs/pool_sv.rs`, `controller/core/src/svc.rs`, and `controller/program/src/instructions/swap/v2/common.rs`.
- Sanctum INF configures LST value calculators with bounded bidirectional conversions and account suffix validation in `/private/tmp/defillama-source/igneous-labs_inf-1.5/sol-val-calc/core/src/traits.rs`, `controller/core/src/typedefs/lst_state.rs`, `controller/program/src/instructions/admin/set_sol_value_calculator.rs`, `sol-val-calc/spl/core/src/calc.rs`, and `sol-val-calc/marinade/core/src/calc.rs`.

## Related Patterns

- [Exchange-Rate Valuation Risk](../oracles/risk-exchange-rate-valuation.md)
- [Conservative AMM LP Collateral Oracle](../oracles/pattern-conservative-amm-lp-collateral-oracle.md)
- [Instruction-Paired Rebalance Solvency Record](./pattern-instruction-paired-rebalance-solvency-record.md)
