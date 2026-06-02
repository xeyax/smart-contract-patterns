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
