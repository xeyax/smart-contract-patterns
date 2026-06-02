# Orderbook-Backed AMM Inventory Accounting

> Account for AMM liquidity deployed to an external orderbook by reconciling vault balances, open orders, unsettled fills, and protocol PnL.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, orderbook, inventory, open-orders, accounting |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- An AMM posts some pool inventory as maker orders on an external orderbook
- Deposits, withdrawals, swaps, or fees depend on total pool inventory
- Maker fills may remain unsettled in open-orders accounts
- Migration or shutdown must settle external market state

## Avoid When

- All pool assets remain inside local vaults
- The orderbook cannot expose reliable open-orders and unsettled-balance state
- Accounting cannot tolerate stale event queues or failed settlement

## Trade-offs

**Pros:**
- Prevents LP accounting from ignoring assets sitting in open orders
- Makes maker PnL and unsettled fills part of pool solvency checks
- Supports safe migration only after external inventory is reconciled

**Cons:**
- External orderbook state becomes part of the AMM trust boundary
- Settlement liveness can affect deposits and withdrawals
- Account-role mistakes can corrupt inventory calculations

## How It Works

For every value-bearing operation, compute inventory from all locations:

```
total_coin = coin_vault + open_orders_coin + unsettled_coin - protocol_coin_pnl
total_pc   = pc_vault   + open_orders_pc   + unsettled_pc   - protocol_pc_pnl
```

LP minting, burning, swap pricing, and migration checks use reconciled totals rather than raw vault balances.

## Key Points

- Reconcile vault balances and open-orders balances before LP share math.
- Subtract protocol PnL or fee reserves before pricing user claims.
- Force cancel/settle before migration or permanent shutdown.
- Validate orderbook, market, vault, and open-orders accounts as one cohort.
- Test stale fills, unsettled maker balances, and failed settlement paths.

## Source Evidence

- Raydium AMM calculates exact vault inventory including Serum/OpenBook open-orders balances.
- Deposit and swap paths use reconciled total inventory rather than vault balances alone.
- Migration logic checks order settlement state before moving away from the external market.

## Related Patterns

- [Invariant-Delta Liquidity Accounting](./pattern-invariant-delta-liquidity-accounting.md)
- [Bounded Cranked Orderbook Maintenance](./pattern-bounded-cranked-orderbook-maintenance.md)
- [Solana Account Cohort Validation](../access-control/pattern-solana-account-cohort-validation.md)
