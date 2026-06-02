# Bounded Cranked Orderbook Maintenance

> Maintain external AMM maker orders through resumable cranks with per-call limits, stored cursors, and cancel/settle fallbacks.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, orderbook, crank, keeper, gas-bounds |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- An AMM maintains many external maker orders
- Order placement, cancellation, and settlement can exceed one transaction budget
- Anyone or a keeper set can progress maintenance
- Stale order plans need cancellation or recalculation

## Avoid When

- The pool uses only local swap math and no external orderbook
- Order maintenance must be fully atomic
- External market settlement cannot be safely resumed

## Trade-offs

**Pros:**
- Avoids gas or compute denial of service in order maintenance
- Makes partially completed order plans recoverable
- Gives operators a bounded emergency cancel/settle path

**Cons:**
- Pool state can spend time between maintenance phases
- Stale cursors and order plans need careful invalidation
- Keepers can influence when maker inventory is refreshed

## How It Works

Split maintenance into small steps:

1. Plan desired orders from current pool state.
2. Cancel stale or excess orders up to a per-call limit.
3. Settle fills.
4. Place new orders up to a per-call limit.
5. Store cursors so the next call resumes safely.

```solidity
function crank(uint256 maxOrders) external {
    uint256 processed;
    while (processed < maxOrders && _hasPendingOrderWork()) {
        _processNextOrderWork();
        processed++;
    }
}
```

## Key Points

- Store plan phase and cursor in pool state.
- Cap order count per call and reject values above protocol maximums.
- Recompute or invalidate plans after price, inventory, or market changes.
- Provide a forced cancel/settle path for shutdown and migration.
- Test partial progress, stale plans, repeated cranks, and keeper failure.

## Source Evidence

- Raydium AMM monitor and order maintenance paths process cancel/place work through bounded steps and stored plan cursors.
- Raydium enforces maximum order limits and includes cancel/settle fallback behavior around external market maintenance.

## Related Patterns

- [Orderbook-Backed AMM Inventory Accounting](./pattern-orderbook-backed-amm-inventory-accounting.md)
- [Unbounded Iteration](../../ANTIPATTERNS.md#unbounded-iteration)
- [Read-Only Protocol Health Checker](../monitoring/pattern-read-only-protocol-health-checker.md)
