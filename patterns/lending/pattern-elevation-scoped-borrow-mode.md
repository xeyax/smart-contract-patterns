# Elevation-Scoped Borrow Mode

> Allow higher borrow power only inside a constrained collateral group with bounded debt assets and explicit group-level risk limits.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, risk-mode, correlated-collateral, ltv, isolation |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A lending market wants higher LTV for tightly related collateral
- The risk mode can restrict collateral assets, debt assets, and collateral count
- Group-level exposure can be tracked separately from ordinary reserves
- Liquidation math can validate the mode's thresholds and close factors

## Avoid When

- Correlated collateral is treated as independent without aggregate limits
- Users can freely mix elevated collateral with unrelated debt
- Oracle and liquidation paths cannot identify the active group

## Trade-offs

**Pros:**
- Gives capital efficiency to known collateral sets without raising global risk
- Keeps elevated debt exposure bounded by a named mode
- Makes correlated-collateral assumptions explicit in code and tests

**Cons:**
- Misconfigured groups can concentrate systemic risk
- Users need clear rules for entering, leaving, and refreshing group state
- Liquidation and borrow checks become more complex

## How It Works

An account opts into a risk group. The protocol enforces that group on every collateral and debt refresh:

```solidity
struct RiskGroup {
    uint256 debtCategory;
    uint256 maxCollateralCount;
    uint256 debtLimit;
    mapping(address => bool) allowedCollateral;
}
```

Borrowing under the group is allowed only for assets in the group debt category,
only while collateral belongs to the group, and only below group exposure limits.

## Key Points

- Validate group parameters before activation: LTV, liquidation threshold, bonus, debt asset set, and asset count.
- Track group debt separately from ordinary reserve debt.
- Recompute group eligibility on collateral deposit, withdrawal, borrow, repay, and price refresh.
- Define how accounts exit elevated mode before borrowing unrelated assets.
- Stress correlated collateral together; do not assume diversification inside the group.

## Source Evidence

- Kamino Lend models `ElevationGroup` with constrained collateral and debt parameters.
- Borrow and deposit refresh paths enforce group membership and group debt rules.
- Market update handlers validate new elevation-group parameters before use.
- Zest Protocol e-mode checks collateral and debt asset type membership when entering the mode, rejects borrows outside the active mode type, and tests mode entry, borrow, and disable-health behavior in `/private/tmp/defillama-source/Zest-Protocol__zest-contracts/onchain/contracts/borrow/production/pool/pool-borrow.clar` and `onchain/tests/borrow/emode.test.ts`.
- Aave V3 eMode supports a bounded category of correlated debt assets rather
  than a single debt token, with validation and tests in `/private/tmp/defillama-source/aave__aave-v3-core/contracts/protocol/libraries/logic/GenericLogic.sol:76`,
  `/private/tmp/defillama-source/aave__aave-v3-core/contracts/protocol/libraries/logic/ValidationLogic.sol:214`,
  and `/private/tmp/defillama-source/aave__aave-v3-core/test-suites/emode.spec.ts:71`.

## Related Patterns

- [Reserve Exposure Caps](./pattern-reserve-exposure-caps.md)
- [Collateral Threshold Separation Requirements](./req-collateral-threshold-separation.md)
- [Correlated Collateral Basket](../../ANTIPATTERNS.md#correlated-collateral-basket)
