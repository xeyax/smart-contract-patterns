# Risk-Priority Liquidation Sequencing

> Force liquidations in multi-asset accounts to address the riskiest debt and weakest collateral before safer legs.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, liquidation, priority, collateral, bad-debt |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Borrower accounts can hold multiple debt and collateral assets
- Liquidators can choose which debt to repay and collateral to seize
- Some positions are undercollateralized, dust, or beyond close-factor thresholds
- The protocol wants to prevent liquidator cherry-picking

## Avoid When

- Each market has exactly one borrow asset and one collateral set
- Liquidation choice is intentionally auctioned as a whole position
- The risk engine cannot rank debt and collateral consistently

## Trade-offs

**Pros:**
- Directs liquidation effort to the legs that reduce insolvency fastest
- Reduces incentives to take only safe collateral while leaving bad debt
- Makes dust and full-liquidation transitions explicit

**Cons:**
- Requires deterministic risk ranking and clear error messages
- Can reduce liquidator flexibility and fill probability
- More edge cases around ties, stale prices, and tiny balances

## How It Works

The protocol computes the account's liquidation reason and required liquidation priority before accepting a repay/seize pair:

```solidity
function liquidate(address account, address debt, address collateral, uint256 repay) external {
    Priority memory p = _requiredPriority(account);

    require(debt == p.debtAsset, "repay higher-risk debt first");
    require(collateral == p.collateralAsset, "seize weakest collateral first");
    require(repay <= _closeFactor(account, p), "above close factor");

    _applyLiquidation(account, debt, collateral, repay);
}
```

## Key Points

- Define deterministic debt and collateral priority for unhealthy accounts.
- Include dust rules so tiny residual debt or collateral cannot block cleanup.
- Recompute priority with fresh prices and indexes before liquidation.
- Test attempts to liquidate lower-risk debt or stronger collateral first.
- Keep close-factor, liquidation cap, and bad-debt realization logic consistent with priority rules.

## Source Evidence

- Kamino Lend's liquidation operations select liquidation reason and reject repay/seize choices that violate required priority.
- Its liquidation logic combines priority checks with close-factor, cap, dust, and full-liquidation paths.

## Related Patterns

- [Dust-Aware Liquidation Cap](./pattern-dust-aware-liquidation-cap.md)
- [Explicit Bad Debt Realization](./pattern-explicit-bad-debt-realization.md)
- [Toxic Liquidation Spiral](../../ANTIPATTERNS.md#toxic-liquidation-spiral)
