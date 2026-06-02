# Action-Scoped NAV Range Accounting

> Maintain midpoint, minimum, and maximum debt valuations so deposits and withdrawals use conservative NAV views for their action.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, nav, oracle, withdrawal, deposit, debt |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Vault assets include external positions whose realizable value is a range
- Deposits should be priced conservatively against incoming users
- Withdrawals should be priced conservatively against exiting users
- Stale destination reports can be recalculated from safe floor or ceiling prices

## Avoid When

- The vault has only idle assets or a single exact exchange-rate position
- Action-specific NAV would be impossible for integrators to reproduce
- Min/max values are discretionary manager inputs rather than bounded oracle or report outputs
- Withdrawals cannot tolerate pulling from multiple destination queues

## Trade-offs

**Pros:**
- Reduces value transfer between entering, exiting, and remaining holders
- Makes stale-report handling explicit by action
- Lets withdrawal logic over-pull conservatively from uncertain external positions

**Cons:**
- More accounting state than a single `totalAssets()`
- Requires exact documentation of which NAV view each action uses
- Ordered destination pulls can be complex and gas-sensitive

## How It Works

Track three debt values for each destination:

```solidity
struct DestinationInfo {
    uint256 cachedDebtValue;
    uint256 cachedMinDebtValue;
    uint256 cachedMaxDebtValue;
    uint256 lastReport;
    uint256 ownedShares;
}
```

The vault exposes action-scoped total assets:

```solidity
function totalAssets(Purpose purpose) public view returns (uint256) {
    if (purpose == Purpose.Global) return idle + debtMid;
    if (purpose == Purpose.Deposit) return idle + debtMax;
    if (purpose == Purpose.Withdraw) return idle + debtMin;
}
```

If reports are stale, recalculate using conservative current floor or ceiling prices and choose the value that is most conservative for the requested action. Withdrawals then pull from an ordered destination queue, using minimum debt values and slippage-aware retry logic before burning shares.

## Key Points

- Document the NAV purpose used for deposit, mint, withdraw, redeem, fee, and display paths.
- Store min and max destination debt alongside midpoint debt at every report.
- Recompute stale reports with action-specific conservative prices, not a generic current price.
- Use withdrawal queues and bounded destination counts so pulling external positions cannot become unbounded.
- Burn shares using the larger of actual assets received and debt value burned when that protects remaining holders.
- Test stale reports, floor/ceiling price moves, partial destination pulls, slippage retries, idle top-ups, and queue exhaustion.

## Source Evidence

- Tokemak Autopool exposes global, deposit, and withdrawal total-asset purposes that use midpoint, maximum, and minimum debt ranges in `/private/tmp/defillama-source/Tokemak__v2-core-pub/src/vault/libs/Autopool4626.sol`.
- Tokemak stores destination midpoint/min/max debt reports, recalculates stale reports conservatively, and pulls withdrawal liquidity from ordered destination debt in `/private/tmp/defillama-source/Tokemak__v2-core-pub/src/vault/libs/AutopoolDebt.sol`.

## Real-World Examples

- Tokemak V2 Autopool - action-scoped NAV ranges for deposits, withdrawals, and global accounting.

## Related Patterns

- [Delta NAV Share Accounting](./pattern-delta-nav.md)
- [Action-Scoped Bounded Risk Prices](../oracles/pattern-action-scoped-bounded-lending-prices.md)
- [Withdrawal Liquidity Buffer](./pattern-withdrawal-liquidity-buffer.md)
