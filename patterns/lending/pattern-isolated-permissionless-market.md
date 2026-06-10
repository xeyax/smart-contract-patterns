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

## Trade-offs

**Pros:**
- Per-market-id accounting contains a bad oracle, token, or insolvency to one market — no cross-market contagion.
- Hash-derived ids from immutable params make markets trustlessly identifiable and impossible to repoint after liquidity exists.
- Governance only curates parameter classes, removing the listing bottleneck and the pressure to underwrite every token.
- A minimal immutable core with market-specific risk pushed to the edges keeps the audit target small and stable.

**Cons:**
- Risk evaluation shifts to users and curators; "enabled parameter classes" is easily misread as governance endorsement of a market.
- Liquidity fragments across many isolated markets for the same asset pair, worsening rates and depth versus pooled designs.
- Nothing in-protocol stops creation of markets with weak oracles or hostile tokens within enabled classes — scam markets are a UX/curation problem by construction.
- Immutable params mean a broken oracle or rate model cannot be fixed; the market can only be abandoned and migrated.
- One-shot permissionless initialization paths must be keyed to market params, or a front-runner sets someone else's market economics.

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
- If a market parameter is initialized permissionlessly only once, key that
  initialization to immutable market parameters and reject subsequent changes.
  One-shot public setup is only safe when the initializer cannot choose someone
  else's market economics.

## Source Evidence

- Morpho Blue uses hashed market parameters, enabled IRM/LLTV guards, and formal market-independence checks for permissionless isolated markets; oracle and token safety remain market-specific user assumptions.
- Morpho Blue fixed-rate IRM allows public one-shot rate initialization keyed by
  market parameters and rejects later changes in [`src/fixed-rate-irm/interfaces/IFixedRateIrm.sol:24`](https://github.com/morpho-org/morpho-blue-irm/blob/a1a87fd5a7ee13873ea9d2bbd87e9c7b2cdbbef3/src/fixed-rate-irm/interfaces/IFixedRateIrm.sol#L24)
  and [`src/fixed-rate-irm/FixedRateIrm.sol:40`](https://github.com/morpho-org/morpho-blue-irm/blob/a1a87fd5a7ee13873ea9d2bbd87e9c7b2cdbbef3/src/fixed-rate-irm/FixedRateIrm.sol#L40).

## Related Patterns

- [Comptroller Risk Gate](./pattern-comptroller-risk-gate.md)
- [Explicit Bad-Debt Realization](./pattern-explicit-bad-debt-realization.md)
- [Permissionless Market Without Guardrails](../../ANTIPATTERNS.md#permissionless-market-without-guardrails)
