# Liquidation Grace Period With Bad-Debt Escape

> Delay ordinary liquidations after an asset freeze or incident, but allow immediate liquidation when the account is already bad debt.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, liquidation, grace-period, bad-debt, freeze |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | High |

## Use When

- A market needs a freeze or grace period after oracle, collateral, or market incidents
- Ordinary liquidations during the grace period may be unfair or destabilizing
- Insolvent accounts should still be resolvable before losses grow
- The protocol can distinguish under-threshold positions from bad debt

## Avoid When

- The protocol cannot compute total debt and collateral value reliably during the incident
- The grace period can be extended indefinitely without governance accountability
- Bad-debt detection relies on the same broken oracle that triggered the grace period

## Trade-offs

**Pros:**
- Gives users and operators time during collateral incidents
- Avoids freezing bad debt into the system
- Makes the liquidation exception explicit and testable

**Cons:**
- More branches in liquidation eligibility
- Incorrect bad-debt detection can bypass intended protection
- Liquidators must understand grace-period state

## How It Works

Gate liquidation on both health and grace-period state:

```solidity
function liquidationAllowed(Position memory p, AssetState memory asset) internal view returns (bool) {
    if (p.healthFactor >= liquidationThreshold) return false;
    if (!asset.gracePeriodEnabled) return true;
    if (p.debtValue > p.collateralValue) return true; // bad-debt escape

    return block.timestamp > asset.freezeEndedAt + asset.gracePeriod;
}
```

The bad-debt branch should be narrow: it should cover accounts whose debt value exceeds collateral value, not merely accounts below the normal liquidation threshold.

### Self-Cure Window Variant

Instead of an asset incident grace period, a lending pool can open a liquidation
state with a fixed grace period in which the borrower can repay enough debt to
return above the liquidation threshold or reduce debt to dust. After the window,
a backstop or stability pool can finalize the liquidation:

```solidity
function closeLiquidation() external {
    require(liquidations[msg.sender].active, "not active");
    require(_isHealthy(msg.sender) || _debtIsDust(msg.sender), "still unsafe");
    delete liquidations[msg.sender];
}
```

The self-cure path should remain risk reducing and must not let the borrower
withdraw collateral while the position is still unsafe.

## Implementation

```solidity
function liquidate(address borrower, address collateral, uint256 repayAmount) external {
    Risk memory risk = _calculateRisk(borrower);
    require(risk.healthFactor < liquidationThreshold, "healthy");
    require(
        !_inGracePeriod(collateral) || risk.debtValue > risk.collateralValue,
        "grace period"
    );

    _repayAndSeize(borrower, collateral, repayAmount);
}
```

### Key Points

- Define the exact bad-debt inequality and test boundary values.
- Keep grace-period parameters asset-specific when incidents are asset-specific.
- Let risk-reducing repay paths remain open during the grace period.
- Monitor grace-period activation and expiry as critical risk events.
- If borrowers can self-cure, define dust thresholds and require the post-cure position to be healthy or economically closed.
- Stability-pool or backstop finalization should run only after grace expiry and should account for any borrower repayments during the window.

## Source Evidence

- Zest Protocol liquidation checks a collateral grace period but bypasses the delay when total borrow value exceeds total collateral value in [`onchain/contracts/borrow/production/pool/liquidation-manager.clar`](https://github.com/Zest-Protocol/zest-contracts/blob/3564bc38906e464ec4de774122bb9bbaee20ddc6/onchain/contracts/borrow/production/pool/liquidation-manager.clar).
- Zest tests cover grace-period liquidation behavior and bad-debt liquidation escape cases in [`onchain/tests/borrow/liquidation-2.test.ts`](https://github.com/Zest-Protocol/zest-contracts/blob/3564bc38906e464ec4de774122bb9bbaee20ddc6/onchain/tests/borrow/liquidation-2.test.ts).
- RAAC `LendingPool.sol` initiates liquidation, allows borrower self-cure through `closeLiquidation`, and restricts finalization to the stability pool after the grace period in [`contracts/core/pools/LendingPool/LendingPool.sol`](https://github.com/tinnohofficial/2025-02-raac/blob/dd5516a9b318b797f82015ee63170d9064514b16/contracts/core/pools/LendingPool/LendingPool.sol).

## Real-World Examples

- Zest Protocol - Clarity lending liquidations include an asset-specific grace-period check with an explicit bad-debt bypass.
- RAAC - RWA lending liquidation state includes a borrower self-cure window and stability-pool finalization.

## Related Patterns

- [Dust-Aware Liquidation Cap](./pattern-dust-aware-liquidation-cap.md)
- [Explicit Bad Debt Realization](./pattern-explicit-bad-debt-realization.md)
- [Toxic Liquidation Spiral](../../ANTIPATTERNS.md#toxic-liquidation-spiral)

## References

- See Source Evidence.
