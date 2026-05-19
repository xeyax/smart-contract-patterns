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

### Staking Accounting Report Variant

For LST/LRT accounting reports, the reported value may come from validator counts, cumulative exit/reward counters, coverage balances, and protocol exchange-rate state rather than manual NAV. Apply the same bounded-report principle to those components:

- validate monotonic cumulative counters
- bound validator-count changes
- bound total-backing movement before applying rewards, fees, exits, or coverage pulls
- fail closed or pause risk-increasing paths on large downside moves
- keep any upside override as an explicit privileged path
- cap protocol-fee minting from exchange-rate gains separately from report acceptance

### Future-Effective RWA Checkpoints

RWA NAV feeds may need both an economic timestamp and an effective timestamp. Limit pending future-effective checkpoints, bound per-checkpoint NAV deltas, and expire extrapolated prices so Chainlink-style `updatedAt` values do not hide stale economic data.

## Key Points

- Block ordinary reports while the current NAV is still valid.
- Bound PPS movement by elapsed time, not only absolute delta.
- Expose any emergency or security-council bypass as a trusted path.
- Snapshot NAV inputs used for async request settlement before user-controlled claims.
- Monitor stale NAV, rejected reports, and bypass use.
- Combine with market, redemption, and liquidity checks for collateral use.
- For RWA feeds, expose the economic data timestamp separately from call-time freshness.
- For staking reports, keep accounting-rate guardrails separate from market-price safety.

## Source Evidence

- Lagoon's ERC-7540 vault code blocks valuation updates while NAV is valid, applies annualized PPS guardrails to manual reports, and exposes an explicit security-council bypass path.
- Liquid Collective and Kelp validate staking exchange-rate reports with monotonic counters, validator-count or backing bounds, downside pause behavior, privileged upside overrides, and daily fee-mint caps.
- Superstate USTB separates NAV economic and effective timestamps, bounds per-checkpoint NAV movement, limits pending future-effective reports, and expires extrapolated prices.

## Related Patterns

- [Async Deposit/Withdrawal](./pattern-async-deposit.md)
- [Historical Bounds](../oracles/pattern-historical-bounds.md)
- [Exchange-Rate Valuation Risk](../oracles/risk-exchange-rate-valuation.md)
