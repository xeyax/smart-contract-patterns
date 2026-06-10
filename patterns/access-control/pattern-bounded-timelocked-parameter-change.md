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

## Trade-offs

**Pros:**
- Users get an observable exit window before economic changes take effect
- Hard on-chain bounds cap the blast radius even if governance keys are compromised
- Commit and apply events give off-chain monitors a reliable signal for pending changes
- Staging delay-reductions under the active delay closes the queue-shortening bypass

**Cons:**
- Slows legitimate emergency response unless risk-reducing changes get an explicit immediate-execution carve-out
- Two-transaction commit/apply flow adds operational burden and can strand pending changes nobody applies
- Bound-check and delay-interaction edge cases are easy to get wrong: validating the stored value instead of the proposed input, or queuing under a pending shorter delay
- Numerically bounded but economically meaningless caps, such as a fee limit just under 100 percent, give false assurance
- Pending values, timestamps, and cancellation rules expand the state machine that must be stored, tested, and audited

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
- VVS `CraftsmanAdmin` illustrates a weak wrapper shape: ownership handoff is delayed, but reward-economic calls such as `add`, `set`, `distributeSupply`, and `updateStakingRatio` are forwarded immediately in [`contracts/CraftsmanAdmin.sol`](https://github.com/vvs-finance/vvs-farm/blob/acd79b99d88157b9d520eeac92e8c6424ae9d8de/contracts/CraftsmanAdmin.sol).
- TON liquid staking separates halter, approver, interest manager, governor, and sudoer roles, with delayed governor and sudoer requests in [`contracts/governor_requests.func`](https://github.com/ton-blockchain/liquid-staking-contract/blob/1f4e9badbed52a4cf80cc58e4bb36ed375c6c8e7/contracts/governor_requests.func) and `sudoer_requests.func`.
- MetaMorpho delays timelock decreases and market-cap increases while allowing
  cap decreases and guardian revokes as immediate risk reductions in [`src/MetaMorpho.sol:213`](https://github.com/morpho-org/metamorpho/blob/163eb2ae022629d4c35e598a668a30451af25f44/src/MetaMorpho.sol#L213)
  and [`src/MetaMorpho.sol:420`](https://github.com/morpho-org/metamorpho/blob/163eb2ae022629d4c35e598a668a30451af25f44/src/MetaMorpho.sol#L420).
- GHO stewards use bounded cooldown/debounce controls after immediate execution,
  which is useful for limiting update cadence but is weaker than a queued
  timelock in [`src/contracts/misc/GhoAaveSteward.sol:80`](https://github.com/aave/gho-core/blob/c6335a0bb9cba099960c5378b1ff0db190b8da8f/src/contracts/misc/GhoAaveSteward.sol#L80),
  [`src/contracts/misc/GhoGsmSteward.sol:52`](https://github.com/aave/gho-core/blob/c6335a0bb9cba099960c5378b1ff0db190b8da8f/src/contracts/misc/GhoGsmSteward.sol#L52),
  and [`docs/gho-stewards.md`](https://github.com/aave/gho-core/blob/c6335a0bb9cba099960c5378b1ff0db190b8da8f/docs/gho-stewards.md).
- Curve Crypto delayed parameter commits and bounded ramps are implemented in
  [`contracts/two/CurveCryptoSwap2.vy:1121-1268`](https://github.com/curvefi/curve-crypto-contract/blob/d7d04cd9ae038970e40be850df99de8c1ff7241b/contracts/two/CurveCryptoSwap2.vy#L1121-L1268),
  while StableSwap NG's immediate bounded fee setter appears in
  [`contracts/main/CurveStableSwapNG.vy:1861-1875`](https://github.com/curvefi/stableswap-ng/blob/2abe778f40206a6c0fd108a0a53ad3266cbedeee/contracts/main/CurveStableSwapNG.vy#L1861-L1875).

## Related Patterns

- [Two-Step Authority Handoff](./pattern-two-step-authority-handoff.md)
- [Break-Glass Risk Limiter](./pattern-break-glass-risk-limiter.md)
- [Unrestricted Admin](../../ANTIPATTERNS.md#unrestricted-admin)
