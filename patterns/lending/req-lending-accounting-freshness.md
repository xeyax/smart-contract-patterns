# Lending Accounting Freshness Requirements

> Requirements for lending markets whose interest, exchange rates, and risk checks update lazily.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, interest, freshness, accrual, accounting |
| Type | Requirement |

## R1: Accrue Before Value-Changing Actions

**A market must bring interest and reserves current before mint, borrow, redeem, repay, or liquidation changes state.**

```
accrualBlock == block.number
```

### What This Means

- Exchange rates use current interest.
- Borrow balances reflect the latest global borrow index.
- Reserves and total borrows are updated before user-visible accounting changes.

## R2: Freshness Scope Is Explicit

**The protocol documents which checks use freshly accrued state and which use stored snapshots.**

### What This Means

- Single-market actions can require same-block accrual.
- Cross-market liquidity may intentionally use stored balances for gas reasons.
- Audits and tests must distinguish local market freshness from account-wide risk freshness.
- View helpers should make clear whether they return raw stored state or expected accrued state.

## R3: Stale Actions Fail Closed

**If accrual fails, value-changing actions revert instead of proceeding with stale state.**

### What This Means

- Interest model errors block the action.
- Oracle failures in exchange-rate or liquidity checks block the action.
- Liquidations do not use stale collateral or debt accounting.
- If liquidation falls back to a cached exchange rate when an oracle call fails,
  that fail-open policy must be explicit, bounded, and covered by tests; it
  should not be an accidental side effect of a broad try/catch.

## R4: Parameter Changes Accrue First

**Rate, index, and accumulator parameters should only change after the affected accumulator is current.**

### What This Means

- Governance cannot change a rate parameter and retroactively apply it over stale time.
- Joining or configuring a market fails closed if required accumulators are stale.
- Tests cover parameter changes before and after accrual.

## R5: Stale Collateral Reports Have Explicit Consequences

**If collateral reporting is required to prove solvency, missed or stale updates must either fail closed for risk-increasing actions or apply a documented penalty/default rule.**

### What This Means

- Collateral update timestamps are monotonic and signer-specific where validator signatures are used.
- Missed update intervals produce an explicit consequence such as freezing, penalty accrual, zero collateral, or action blocking.
- Penalties accrue from the same indexed debt base as ordinary interest, so stale reporting cannot understate liabilities.
- Tests cover the transition from fresh, to missed interval, to stale/default state.

## Verification Checklist

| Requirement | Question |
|-------------|----------|
| R1 | Does every mint/borrow/redeem/repay/liquidate path accrue first? |
| R2 | Are stored snapshot reads clearly documented? |
| R3 | Can stale accrual be bypassed through a secondary entry point? |
| R4 | Do rate/index parameter changes force current accrual first? |
| R5 | Do stale collateral reports fail closed or apply explicit penalties/default rules? |

## Source Evidence

- JustLend accrues interest before mint, borrow, redeem, and liquidation paths and checks same-block freshness before state transitions.
- Its comptroller liquidity checks use stored snapshots for cross-market calculations, showing why freshness scope must be explicit.
- Morpho Blue accrues before supply, withdraw, borrow, repay, liquidation, and fee changes, and its formal specs compare explicit pre-accrual with expected accrued state; collateral-supply paths that intentionally skip accrual are outside debt-index freshness.
- Aave V3 updates reserve state before value-changing reserve actions and represents user balances through indexes that depend on current reserve accounting.
- Sky/Maker DSS rate accumulator modules require current accumulators before changing duty or savings rates and test stale-parameter-change failures.
- Compound V2 requires market interest accrual to be current before borrow, repay, redeem, and liquidation state transitions, with debt represented as principal plus borrower interest index in `CToken.sol`.
- Aave V2 calls reserve `updateState` before deposit, withdraw, borrow, repay, and flash-loan debt conversion paths, with reserve indexes updated from timestamped state in `/private/tmp/defillama-source/aave__protocol-v2/contracts/protocol/lendingpool/LendingPool.sol` and `ReserveLogic.sol`.
- M0's minter gateway validates sorted validator signatures and monotonic signer timestamps for collateral updates, then applies missed-update and undercollateralization penalties through indexed active owed M in `/private/tmp/defillama-source/m0-foundation__protocol/src/MinterGateway.sol` and integration tests under `test/integration/minter-gateway/update-collateral`.
- Abracadabra Cauldron V3 demonstrates why cached-price fallback during
  liquidation needs an explicit stale-price policy: exchange-rate updates and
  liquidation paths interact through `/private/tmp/defillama-source/abracadabra-money__magic-internet-money/contracts/CauldronV3.sol:203-217`
  and `/private/tmp/defillama-source/abracadabra-money__magic-internet-money/contracts/CauldronV3.sol:500-508`.

## Related Patterns

- [Lazy Borrow Index](./pattern-lazy-borrow-index.md)
- [Comptroller Risk Gate](./pattern-comptroller-risk-gate.md)
- [Scaled Balance Token Accounting](./pattern-scaled-balance-token-accounting.md)
- [Share-Denominated Lending Accounting](./pattern-share-denominated-lending-accounting.md)
