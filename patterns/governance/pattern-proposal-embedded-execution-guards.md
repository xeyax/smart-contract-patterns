# Proposal-Embedded Execution Guards

> Include guard calls inside executable governance proposals so final dynamic conditions are checked atomically at execution time.

## Metadata

| Property | Value |
|----------|-------|
| Category | governance |
| Tags | governance, timelock, proposal, guard, execution |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Proposal validity depends on dynamic state at execution time
- Timelock delay, executor migration, or dependency wiring can change after proposal creation
- Off-chain review cannot prove final conditions will still hold
- A revert is safer than partially executing under changed assumptions

## Avoid When

- The guard can be bypassed by alternate executors
- Guard reads are manipulable in the same transaction
- Proposal execution must never revert after approval
- Static target/selector allowlists are enough

## Trade-offs

**Pros:**
- Final conditions are checked atomically at execution time, closing the gap between off-chain review and on-chain reality.
- A revert before the sensitive action is strictly safer than partial execution under changed assumptions.
- Guards are read-only view calls — cheap to write, cheap to execute, no new privileged roles.
- No timelock or executor contract changes needed; protection lives entirely in proposal payloads.

**Cons:**
- Protection is per-proposal and opt-in: a proposal author who omits the guard gets none, so review burden shifts to payload construction.
- Guards reading manipulable state (market prices, balances) can be gamed in the same transaction or used to grief execution.
- Approved proposals can become permanently unexecutable if the guarded condition never re-holds, requiring re-proposal through the full governance cycle.
- Alternate executors or migration paths can bypass guard calls entirely, giving false assurance.
- Testing must cover changed final state, not just creation-time state, expanding the proposal QA matrix.

## How It Works

Add guard calls as proposal actions before value-changing actions:

```solidity
function assertDelayAtLeast(uint256 minDelay) external view {
    require(timelock.getMinDelay() >= minDelay, "delay changed");
}
```

If the execution environment changed during the governance delay, the proposal reverts before executing the sensitive action.

## Key Points

- Put guard calls before the actions they protect.
- Make guard functions read-only and deterministic.
- Guard against executor, timelock, permission, and dependency changes.
- Avoid guards that depend on easily manipulated market state.
- Test proposals against changed final state, not only creation-time state.

## Source Evidence

- Lido Dual Governance deployment and launch tooling uses executable guard checks to ensure proposal timing and migration assumptions still hold when the proposal runs.

## Related Patterns

- [Bounded Timelocked Parameter Change](../access-control/pattern-bounded-timelocked-parameter-change.md)
- [Governance as Arbitrary Execution](../../ANTIPATTERNS.md#governance-as-arbitrary-execution)
