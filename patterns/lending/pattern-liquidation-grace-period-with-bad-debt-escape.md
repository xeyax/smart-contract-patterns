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

## Source Evidence

- Zest Protocol liquidation checks a collateral grace period but bypasses the delay when total borrow value exceeds total collateral value in `/private/tmp/defillama-source/Zest-Protocol__zest-contracts/onchain/contracts/borrow/production/pool/liquidation-manager.clar`.
- Zest tests cover grace-period liquidation behavior and bad-debt liquidation escape cases in `/private/tmp/defillama-source/Zest-Protocol__zest-contracts/onchain/tests/borrow/liquidation-2.test.ts`.

## Real-World Examples

- Zest Protocol - Clarity lending liquidations include an asset-specific grace-period check with an explicit bad-debt bypass.

## Related Patterns

- [Dust-Aware Liquidation Cap](./pattern-dust-aware-liquidation-cap.md)
- [Explicit Bad Debt Realization](./pattern-explicit-bad-debt-realization.md)
- [Toxic Liquidation Spiral](../../ANTIPATTERNS.md#toxic-liquidation-spiral)

## References

- See Source Evidence.
