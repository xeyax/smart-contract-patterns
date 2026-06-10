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

## Trade-offs

**Pros:**
- Annualized PPS bounds cap the damage of a fat-fingered or malicious report to one bounded step instead of an arbitrary jump.
- Validity windows make staleness explicit: settlement either uses a live NAV or fails, rather than silently pricing on old data.
- Fail-closed downside behavior pauses risk-increasing paths before a bad report propagates into mints and redemptions.
- Privileged bypass and one-shot overrides are explicit, evented paths, so legitimate out-of-band moves stay auditable instead of widening the ordinary bounds.
- The same bounded-report skeleton extends to staking counters, signed uploads, RWA checkpoints, and liability rates without new trust assumptions.

**Cons:**
- Reporter is still trusted within the bounds: a manager can drift NAV by the maximum allowed rate every period and guardrails prove nothing about real backing or market realizability.
- Legitimate fast moves (genuine loss, market crash) get rejected or forced through the bypass, so the trusted path gets exercised exactly when scrutiny is lowest.
- Users settle against discrete, expiring NAV — no instant settlement, and claims queue until a fresh valid report lands.
- Operational dependence on report cadence: a missed report expires the NAV and can halt conversions protocol-wide.
- Each variant (monotonic counters, dual timestamps, signed payloads, cooldowns, liability rates) adds its own parameter set and failure modes; tuning bounds too tight bricks reporting, too loose voids the protection.
- Component-level decomposition checks are extra audit surface — an aggregate-only check passes while pending-exit or reserve splits are wrong.

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

### Signed Exchange-Rate Upload Variant

For off-chain exchange-rate uploads, the signed payload should bind the chain,
contract, exchange rate, deadline, and report timestamp. The on-chain upload path
should reject expired signatures, excessive per-period update counts, and
exchange-rate moves outside configured bounds before the rate can affect mint,
redeem, or withdrawal settlement.

### One-Shot Override Variant

Strategy health checks sometimes need an explicit one-shot override after a
legitimate out-of-band gain or loss. Treat the override as a privileged event
that applies to one report only, then clear it automatically so routine reports
return to bounded acceptance.

### External-Core Cooldown Variant

If exchange-rate accounting depends on an external staking core, block rate
updates until the core has completed a minimum delay or checkpoint after deposits,
withdrawals, or operator accounting changes. The cooldown reduces same-block or
same-epoch accounting races, but it does not prove the external core's value.

### Liability-Rate Vault Variant

Some vaults compute `totalAssets()` and ERC4626 conversions from a managed
liability rate rather than from current token balance. Apply report cadence,
minimum/maximum rate, and per-update delta bounds to that rate, and document that
the contract balance can diverge from accounting assets while operators move
assets externally.

## Key Points

- Block ordinary reports while the current NAV is still valid.
- Bound PPS movement by elapsed time, not only absolute delta.
- Expose any emergency or security-council bypass as a trusted path.
- Snapshot NAV inputs used for async request settlement before user-controlled claims.
- Monitor stale NAV, rejected reports, and bypass use.
- Combine with market, redemption, and liquidity checks for collateral use.
- For RWA feeds, expose the economic data timestamp separately from call-time freshness.
- For staking reports, keep accounting-rate guardrails separate from market-price safety.
- For shared price calculators, pause conversions or risk-increasing actions when a report violates age, cadence, or movement thresholds.
- Simulate complex oracle reports before applying them, and separately account burn-cover buckets from ordinary fee or reward accounting.
- Signed NAV or exchange-rate reports should bind chain id and verifying contract, enforce signature expiry, and cap update frequency as well as value movement.
- One-shot report overrides should clear after one use and be monitored as privileged bypasses.
- External-core exchange-rate updates should enforce a cooldown or checkpoint before rate changes affect user settlement.
- Liability-rate vaults should fuzz conversion round trips and make rate updates role-bound, cadence-bound, and pause-aware.
- Snapshot reports that decompose total backing into component balances need component-level sanity checks; a correct aggregate NAV can still hide wrong pending-exit, reserve, or staking-core decomposition.

## Source Evidence

- Lagoon's ERC-7540 vault code blocks valuation updates while NAV is valid, applies annualized PPS guardrails to manual reports, and exposes an explicit security-council bypass path.
- Liquid Collective and Kelp validate staking exchange-rate reports with monotonic counters, validator-count or backing bounds, downside pause behavior, privileged upside overrides, and daily fee-mint caps.
- Superstate USTB separates NAV economic and effective timestamps, bounds per-checkpoint NAV movement, limits pending future-effective reports, and expires extrapolated prices.
- Lido simulates oracle reports, caps positive rebases, rejects large consensus-layer losses through sanity checks, and tracks cover/non-cover share-burn buckets in [`contracts/0.8.9`](https://github.com/lidofinance/core/blob/c1250690f0b37202464cd4fb68e64ad6720328a4/contracts/0.8.9).
- Aera v3 price reports enforce max price age, monotonic timestamps, minimum update interval, maximum update delay, upward/downward tolerance ratios, and automatic pause on threshold violation in [`v3/src/core/PriceAndFeeCalculator.sol`](https://github.com/aera-finance/aera-contracts-public/blob/9888a9e0d50fa38d4e86a69a8ebb9b605b08dafd/v3/src/core/PriceAndFeeCalculator.sol).
- Astherus `Earn.sol` accepts signed exchange-rate uploads in `uploadExchangeRate`, binding expiry and chain-specific message data while enforcing configured update cadence and deviation limits in [`contracts/Earn.sol`](https://github.com/astherus-contract/astherus-earn-contract/blob/1472bad4d7267a2c9dbf490b646201ad673e9285/contracts/Earn.sol).
- Yearn V3 periphery bounds strategy report profit and loss and supports one-shot overrides in [`src/Bases/HealthCheck/BaseHealthCheck.sol`](https://github.com/yearn/tokenized-strategy-periphery/blob/8d940ecc518c9b4e198e240cca634f315f37e318/src/Bases/HealthCheck/BaseHealthCheck.sol).
- EtherFi beHYPE uses staking-core accounting cooldowns before exchange-rate updates in [`src/StakingCore.sol`](https://github.com/etherfi-protocol/beHYPE/blob/06ee135254508fa3f0ab6b1bd8e80dc805884420/src/StakingCore.sol).
- Ember Vault stores a managed rate, enforces update interval, min/max rate, and max per-update delta, and derives `totalAssets()` and conversions from that rate in [`contracts/EmberVault.sol`](https://github.com/ember-protocol/Ember-Vaults-EVM/blob/11ce048163338d944677e22f811dbd80eaf094c6/contracts/EmberVault.sol), with rate-bound and conversion fuzz tests under [`test`](https://github.com/ember-protocol/Ember-Vaults-EVM/blob/11ce048163338d944677e22f811dbd80eaf094c6/test).
- Swell `RepricingOracle` implementations report exchange-rate data for LST/LRT exit accounting in [`contracts/lst/contracts/implementations/RepricingOracle.sol`](https://github.com/SwellNetwork/v3-core-public/blob/ba1eeff12ab994a26492fa5dcd0aa8937733dbb4/contracts/lst/contracts/implementations/RepricingOracle.sol) and [`contracts/lrt/contracts/implementations/RepricingOracle.sol`](https://github.com/SwellNetwork/v3-core-public/blob/ba1eeff12ab994a26492fa5dcd0aa8937733dbb4/contracts/lrt/contracts/implementations/RepricingOracle.sol).

## Related Patterns

- [Async Deposit/Withdrawal](./pattern-async-deposit.md)
- [Historical Bounds](../oracles/pattern-historical-bounds.md)
- [Exchange-Rate Valuation Risk](../oracles/risk-exchange-rate-valuation.md)
