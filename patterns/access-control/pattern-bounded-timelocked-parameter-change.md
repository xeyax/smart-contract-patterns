# Bounded Timelocked Parameter Change

> Require critical parameter changes to be committed, delayed, bounded, and explicitly applied before they affect protocol economics.

## Metadata

| Property | Value |
|----------|-------|
| Category | access-control |
| Tags | access-control, timelock, parameters, bounds, governance |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Parameters affect fees, amplification, rates, caps, or admin recipients
- Users need time to react before a change activates
- A parameter can be bounded by protocol invariants
- Changes should be cancellable or superseded before activation

## Avoid When

- The parameter is harmless or purely cosmetic
- Emergency risk reduction must happen immediately
- Bounds are only social conventions and not enforced on-chain

## How It Works

Stage the change first:

```solidity
function commitFee(uint256 newFee) external onlyGovernance {
    require(newFee <= MAX_FEE, "fee too high");
    pendingFee = newFee;
    applyAfter = block.timestamp + delay;
}

function applyFee() external {
    require(block.timestamp >= applyAfter, "delay");
    fee = pendingFee;
}
```

For continuous changes such as AMM amplification ramps, also bound the maximum rate of change and minimum ramp duration.

### Delay-Reduction Guardrail

If the delay itself is configurable, reductions must be staged under the currently active delay:

```solidity
function commitDelay(uint256 newDelay) external onlyGovernance {
    require(newDelay >= MIN_DELAY, "too short");
    pendingDelay = newDelay;
    delayApplyAfter = block.timestamp + delay; // current delay, not newDelay
}
```

Any config queued while a shorter delay is pending should still use the active delay. Otherwise governance can queue a zero-delay reduction and immediately queue sensitive changes under the pending shorter value.

## Key Points

- Enforce hard bounds in the commit function.
- Emit both commit and apply events.
- Treat delay reductions as critical changes.
- Make cancellation rules explicit.
- Test edge values, early apply attempts, and maximum-change constraints.
- Test that reducing the delay cannot shorten already queued or same-block follow-on changes.
- Test that bounds are applied to the proposed new value, not accidentally to the current stored value or another stale state variable.
- Ensure numeric bounds are economically meaningful; a fee cap just below 100 percent may still be a confiscatory admin power.
- Treat trust-list changes, vault enablement, maintainer admission, and bridge allowlists as critical parameter changes even when the value is boolean.
- Do not label cooldown-bounded updates as timelocks unless users can observe a committed change before it becomes executable.
- Bound claim, cooldown, and processing-period setters with hard upper limits when they affect exit liveness, not only fee or rate economics.
- A wrapper that timelocks only ownership transfer is not a timelock for forwarded economic setters; delay the sensitive calls themselves.
- Split emergency halt, routine operator, governor, and root/sudo powers so immediate roles cannot exercise delayed root authority.
- Treat risk expansion and risk reduction asymmetrically: cap increases and
  timelock decreases should be delayed, while cap decreases or market revokes
  may execute immediately when they can only reduce exposure.
- Cooldown-bounded steward updates that execute immediately and then block the
  next update are rate limits, not user-observable queued timelocks.

## Source Evidence

- Curve Crypto commits and applies parameter changes behind a delay and bounds
  A/gamma ramps by duration and maximum factor changes; StableSwap NG has
  bounded immediate fee setters, so Curve evidence should not be generalized to
  every Curve template.
- An Ondo audit-contest snapshot showed setter checks that appeared to validate current fee variables rather than proposed inputs, a reusable stale-state bound-check failure mode.
- StakeWise V2 audit material flagged a protocol-fee bound just below 100 percent as economically weak despite being numerically bounded.
- tBTC v2 shows that immediate trust-list changes depend on the outer owner or governance path when no internal delay is present.
- Fluid uses cooldown-bounded rate authorization for some changes; this is useful risk reduction but weaker than public commit-and-delay semantics.
- Stake DAO's UniversalBoostRegistry tests delay-reduction bypass attempts by queuing delay changes under the current delay before allowing shorter-delay config changes.
- SlowMist's Avalon USDa audit flagged an unbounded saving-account process-period setter as an exit-liveness risk, reinforcing that time parameters need hard upper bounds.
- VVS `CraftsmanAdmin` illustrates a weak wrapper shape: ownership handoff is delayed, but reward-economic calls such as `add`, `set`, `distributeSupply`, and `updateStakingRatio` are forwarded immediately in `/private/tmp/defillama-source/vvs-finance__vvs-farm/contracts/CraftsmanAdmin.sol`.
- TON liquid staking separates halter, approver, interest manager, governor, and sudoer roles, with delayed governor and sudoer requests in `/private/tmp/defillama-source/ton-blockchain__liquid-staking-contract/contracts/governor_requests.func` and `sudoer_requests.func`.
- MetaMorpho delays timelock decreases and market-cap increases while allowing
  cap decreases and guardian revokes as immediate risk reductions in `/private/tmp/defillama-source/morpho-org__metamorpho/src/MetaMorpho.sol:213`
  and `/private/tmp/defillama-source/morpho-org__metamorpho/src/MetaMorpho.sol:420`.
- GHO stewards use bounded cooldown/debounce controls after immediate execution,
  which is useful for limiting update cadence but is weaker than a queued
  timelock in `/private/tmp/defillama-source/aave__gho-core/src/contracts/misc/GhoAaveSteward.sol:80`,
  `/private/tmp/defillama-source/aave__gho-core/src/contracts/misc/GhoGsmSteward.sol:52`,
  and `/private/tmp/defillama-source/aave__gho-core/docs/gho-stewards.md`.
- Curve Crypto delayed parameter commits and bounded ramps are implemented in
  `/private/tmp/defillama-source/curvefi__curve-crypto-contract/contracts/two/CurveCryptoSwap2.vy:1121-1268`,
  while StableSwap NG's immediate bounded fee setter appears in
  `/private/tmp/defillama-source/curvefi__stableswap-ng/contracts/main/CurveStableSwapNG.vy:1861-1875`.

## Related Patterns

- [Two-Step Authority Handoff](./pattern-two-step-authority-handoff.md)
- [Break-Glass Risk Limiter](./pattern-break-glass-risk-limiter.md)
- [Unrestricted Admin](../../ANTIPATTERNS.md#unrestricted-admin)
