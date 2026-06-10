# Dual-Asset Stability Buffer

> Hold both volatile collateral and stable liquidity so redemptions, rebalances, or liquidations can consume the safest buffer first.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, stablecoin, buffer, rebalance, liquidation |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A stablecoin or lending pool holds yield-bearing or volatile collateral
- The pool also maintains stable liquidity for redemptions or rebalances
- Rebalance and liquidation flows can choose which asset buffer to consume
- Users need minimum collateral-out or minimum stable-out protection

## Avoid When

- The pool has only one asset class and no stable liquidity buffer
- Stable liquidity can be spent without preserving backing or accounting
- Rebalance paths do not enforce user or protocol minimum outputs
- Oracle valuation cannot distinguish the two asset classes safely

## Trade-offs

**Pros:**
- Gives the protocol a softer landing before selling volatile collateral
- Makes stable liquidity usage explicit during stress
- Can reduce liquidation slippage when stable inventory is available

**Cons:**
- Requires careful accounting across two buffers
- Stable inventory can create false confidence if not reserved correctly
- Rebalance ordering becomes a value-affecting policy choice

## How It Works

Track the pool's volatile collateral and stable liquidity separately. During a
rebalance or liquidation, consume the stable buffer first when that reduces risk,
then consume volatile collateral subject to `minOut` bounds.

```solidity
function rebalance(uint256 debtToCover, uint256 minCollateralOut) external {
    uint256 stableUsed = _consumeStableBuffer(debtToCover);
    uint256 remainingDebt = debtToCover - stableUsed;

    uint256 collateralOut;
    if (remainingDebt > 0) {
        collateralOut = _sellCollateralForDebt(remainingDebt);
        require(collateralOut >= minCollateralOut, "collateral out");
    }

    _accountRebalance(stableUsed, collateralOut);
}
```

The oracle layer should value deposits and withdrawals through the same unit of
account, but the liquidation path should still preserve explicit buffer order and
minimum-output checks.

## Implementation

- Separate stable-buffer balances from collateral balances in accounting.
- Define the order in which buffers are consumed for redeem, rebalance, and liquidation.
- Enforce `minOut` or equivalent bounds on volatile collateral movement.
- Keep stable-buffer depletion visible to monitoring and risk parameters.
- Test stable-only, collateral-only, mixed-buffer, depeg, and insufficient-buffer cases.

## Source Evidence

- fx Protocol's fxUSD base pool holds both fxUSD/stable balances and protocol collateral, values deposits through stable oracle paths, consumes stable inventory during rebalance and liquidation paths, and enforces `minCollOut` style protections in [`contracts/core/FxUSDBasePool.sol`](https://github.com/AladdinDAO/fx-protocol-contracts/blob/5e198e93657db008a57129e7eea21a996618f17f/contracts/core/FxUSDBasePool.sol) and `contracts/core/PoolManager.sol`.
- fx Protocol tests cover mixed collateral/stable rebalance behavior in [`test/core/FxUSDBasePool.spec.ts`](https://github.com/AladdinDAO/fx-protocol-contracts/blob/5e198e93657db008a57129e7eea21a996618f17f/test/core/FxUSDBasePool.spec.ts).

## Real-World Examples

- fx Protocol uses a stable/collateral buffer to manage fxUSD redemptions, rebalances, and liquidation flows.

## Related Patterns

- [Explicit Bad Debt Realization](./pattern-explicit-bad-debt-realization.md)
- [Reserve Exposure Caps](./pattern-reserve-exposure-caps.md)
- [Circuit Breaker](../vaults/pattern-circuit-breaker.md)

## References

- fx Protocol core pool contracts.
