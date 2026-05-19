# Isolated Permissionless Market

> Let anyone create lending markets only when each market's collateral, debt, oracle, and interest-rate state is isolated from every other market.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, permissionless, isolated-market, risk, oracle |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- The protocol wants permissionless market creation
- Risk is intentionally scoped to one collateral/loan pair or market id
- Shared governance can approve parameter classes without underwriting every market
- Users can evaluate market-specific oracle, LLTV, and interest-rate choices

## Avoid When

- Markets share collateral liquidity or debt accounting in a way one bad market can drain others
- Any token can be listed without bounds on oracle, LLTV, or rate model
- Liquidation and bad-debt effects are socialized across unrelated markets

## How It Works

Derive market identity from immutable parameters:

```solidity
struct MarketParams {
    address loanToken;
    address collateralToken;
    address oracle;
    address interestRateModel;
    uint256 lltv;
}

function id(MarketParams memory params) internal pure returns (bytes32) {
    return keccak256(abi.encode(params));
}
```

The protocol stores balances and totals under the market id, and only accepts markets whose parameter classes are enabled.

## Key Points

- Isolate supply, borrow, collateral, and bad-debt accounting per market id.
- Require enabled oracle, rate model, and LLTV classes before market creation.
- Make market params immutable once liquidity exists.
- Keep callbacks and hooks from writing unrelated market state.
- Prove or test that one market's insolvency cannot reduce another market's assets.
- Document that enabled parameter classes do not mean governance has underwritten every token/oracle pair; users and curators still evaluate market-specific risk.

## Source Evidence

- Morpho Blue uses hashed market parameters, enabled IRM/LLTV guards, and formal market-independence checks for permissionless isolated markets; oracle and token safety remain market-specific user assumptions.

## Related Patterns

- [Comptroller Risk Gate](./pattern-comptroller-risk-gate.md)
- [Explicit Bad-Debt Realization](./pattern-explicit-bad-debt-realization.md)
- [Permissionless Market Without Guardrails](../../ANTIPATTERNS.md#permissionless-market-without-guardrails)
