# ADL Reserve And Funding Risk Controls

> Requirements for perpetuals markets that use pool liquidity, funding, reserve limits, and auto-deleveraging.

## Metadata

| Property | Value |
|----------|-------|
| Category | perps |
| Tags | perps, adl, funding, reserve, open-interest |
| Type | Requirement |

## R1: Reserve And Open Interest Limits Are Explicit

**Markets must reject actions that push reserved liquidity or open interest beyond configured market limits.**

### What This Means

- Reserve factors are checked per side and per market.
- Open interest reserve checks use current pool value and oracle prices.
- Limit changes are treated as risk parameter changes.

## R2: Funding Rounding Cannot Be Avoided By Tiny Updates

**Funding-fee math must specify rounding and minimum update behavior so tiny updates cannot repeatedly avoid fees.**

### What This Means

- Funding calculations define rounding direction for longs and shorts.
- Tests cover tiny elapsed time, tiny size, and repeated update cases.
- Any zero-fee threshold is intentional and bounded.

## R3: ADL Uses Fresh Oracle State And Explicit Thresholds

**Auto-deleveraging state transitions depend on fresh oracle timestamps and configured pending-PnL thresholds.**

### What This Means

- ADL activation checks use current oracle timestamps.
- Pending PnL is compared against configured factors before ADL orders are valid.
- ADL creation and execution are separate monitored actions.

## R4: Backstop Exhaustion And Socialized Loss Are Explicit

**If insurance, fee pools, or security modules can be exhausted, the protocol must define the next loss-allocation step before insolvency occurs.**

### What This Means

- Backstop balance and depletion checks are explicit.
- Socialized loss, bankruptcy, or deleveraging updates name the accounts or pools affected.
- Tests cover partial backstop use, full exhaustion, and the transition into socialized loss.

## Source Evidence

- GMX Synthetics validates reserves and open-interest reserve factors, implements funding-fee rounding rules, and gates ADL state/order validity on fresh oracle timestamps and pending-PnL thresholds.
- Drift caps reserve-paid funding, uses liquidation and bankruptcy fallback paths, and supports socialized loss through funding/PnL settlement mechanics without being cited as direct ADL evidence.
- Derive V2 uses a security module and cash-asset insolvency accounting with tests for socialized losses after backstop exhaustion.

## Related Patterns

- [Capped PnL Impact Pool Risk Accounting](./pattern-capped-pnl-impact-pool-risk-accounting.md)
- [Fee-Pool Capped Asymmetric Funding](./pattern-fee-pool-capped-asymmetric-funding.md)
- [Oracle Staleness Risk](../oracles/risk-oracle-staleness.md)
