# Rate-Bounded NAV Report

> Accept manual or off-chain NAV reports only after the current NAV expires and only within annualized share-price movement guardrails.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, nav, oracle, reporting, guardrails, erc7540 |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Vault NAV is reported by an off-chain manager, accountant, or security council
- The asset portfolio cannot be priced fully on-chain
- NAV reports should be valid for an explicit window
- Share-price jumps can be bounded by plausible annualized movement

## Avoid When

- On-chain pricing is available and manipulation-resistant
- The manager can bypass guardrails without monitoring or governance review
- NAV can legitimately move faster than the configured bounds
- Users need instant settlement against continuously changing prices

## How It Works

Track the current NAV, its expiry, and bounded movement to the next report:

```solidity
function updateNav(uint256 nextAssets) external onlyReporter {
    require(block.timestamp > navValidUntil, "nav still valid");

    uint256 currentPps = totalAssets * WAD / totalSupply;
    uint256 nextPps = nextAssets * WAD / totalSupply;
    require(_withinAnnualizedBounds(currentPps, nextPps, lastReportAt), "rate bound");

    totalAssets = nextAssets;
    lastReportAt = block.timestamp;
    navValidUntil = block.timestamp + navValidity;
}
```

The guardrail reduces bad reports and operational mistakes. It does not prove NAV accuracy or market realizability.

## Key Points

- Block ordinary reports while the current NAV is still valid.
- Bound PPS movement by elapsed time, not only absolute delta.
- Expose any emergency or security-council bypass as a trusted path.
- Snapshot NAV inputs used for async request settlement before user-controlled claims.
- Monitor stale NAV, rejected reports, and bypass use.
- Combine with market, redemption, and liquidity checks for collateral use.

## Source Evidence

- Lagoon's ERC-7540 vault code blocks valuation updates while NAV is valid, applies annualized PPS guardrails to manual reports, and exposes an explicit security-council bypass path.

## Related Patterns

- [Async Deposit/Withdrawal](./pattern-async-deposit.md)
- [Historical Bounds](../oracles/pattern-historical-bounds.md)
- [Exchange-Rate Valuation Risk](../oracles/risk-exchange-rate-valuation.md)
