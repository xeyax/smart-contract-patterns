# Scenario-Shocked Portfolio Margin

> Compute initial and maintenance margin from worst-case spot, volatility, skew, basis, collateral-haircut, and confidence scenarios.

## Metadata

| Property | Value |
|----------|-------|
| Category | perps |
| Tags | perps, options, portfolio-margin, scenarios, risk |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Accounts hold portfolios of options, perps, cash, and collateral
- Risk cannot be captured by independent per-position margin alone
- The protocol can configure scenario shocks and collateral haircuts
- Worst-case initial and maintenance margin can be computed deterministically

## Avoid When

- Positions are simple enough for isolated margin
- Scenario configuration is opaque or frequently changed without delay
- Oracle confidence or volatility inputs are unavailable
- Users cannot preview margin impact before trade execution

## Trade-offs

**Pros:**
- Captures offsets and concentrations across a portfolio
- Makes volatility, skew, basis, and collateral confidence explicit
- Can support more capital-efficient options and perps markets

**Cons:**
- Configuration is complex and governance-sensitive
- Worst-case calculations can be expensive
- Incorrect scenarios can under-margin correlated stress

## How It Works

Define a set of shock scenarios for the relevant underlier, volatility, skew,
basis, and collateral confidence. Revalue the account under each scenario and
use the worst loss as initial or maintenance margin.

```solidity
function portfolioMargin(Account memory account) internal view returns (uint256 im, uint256 mm) {
    int256 worstInitial;
    int256 worstMaintenance;

    for (uint256 i; i < scenarios.length; i++) {
        Scenario memory s = scenarios[i];
        int256 value = _revaluePortfolio(account, s);
        worstInitial = min(worstInitial, value - s.initialShock);
        worstMaintenance = min(worstMaintenance, value - s.maintenanceShock);
    }

    im = uint256(-worstInitial);
    mm = uint256(-worstMaintenance);
}
```

## Implementation

- Version and timelock scenario parameters.
- Include spot, volatility, skew, basis, and collateral haircut assumptions where relevant.
- Apply oracle confidence contingencies before crediting collateral or PnL.
- Bound the number of scenarios or cache reusable risk arrays.
- Test offset portfolios, concentrated portfolios, stale/confidence-degraded oracle inputs, and worst-scenario selection.

## Source Evidence

- Derive V2 documents portfolio margin risk managers in `/private/tmp/defillama-source/derivexyz__v2-core/docs/managers/PMRM.md`.
- Derive V2 computes spot, volatility, skew, basis, collateral haircut, and confidence scenario risk in `src/risk-managers/PMRM_2.sol` and `src/risk-managers/PMRMLib_2.sol`.
- Derive V2 tests portfolio scenario cases in `test/risk-managers/unit-tests/PMRM_2/TestPMRM_2_PortfolioCasesNEW.t.sol`.

## Real-World Examples

- Derive V2 uses scenario-shocked portfolio margin for options and perps portfolios.

## Related Patterns

- [Position-Size Scaled Margin Requirement](./pattern-position-size-scaled-margin-requirement.md)
- [Open-Interest Scaled Margin Requirement](./pattern-open-interest-scaled-margin-requirement.md)
- [Oracle Reliability Requirements](../oracles/req-oracle-reliability.md)

## References

- Derive V2 portfolio margin docs and source.
