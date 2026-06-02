# Condition-Gated Deadlock Tiebreaker

> Grant a narrow committee recovery powers only after objective deadlock conditions and timeouts prove normal governance cannot progress.

## Metadata

| Property | Value |
|----------|-------|
| Category | governance |
| Tags | governance, recovery, deadlock, tiebreaker, committee |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Governance can become blocked by an exit, pause, or veto state
- Objective on-chain conditions can prove prolonged deadlock
- Recovery powers can be narrowly enumerated
- The committee is more acceptable than indefinite liveness failure

## Avoid When

- The committee can bypass normal governance at any time
- Deadlock conditions are subjective or off-chain only
- Recovery powers can move funds or execute arbitrary proposals
- A monotonic break-glass limiter is sufficient

## How It Works

The tiebreaker checks state and elapsed time before exposing limited recovery actions:

```solidity
modifier onlyAfterDeadlock() {
    require(systemPaused(), "not paused");
    require(block.timestamp >= pausedSince + deadlockTimeout, "too early");
    _;
}

function resumeExitQueue() external onlyTiebreaker onlyAfterDeadlock {
    _resumeExitQueue();
}
```

Unlike a pure break-glass limiter, a deadlock tiebreaker may resume or reseal systems. Its legitimacy depends on narrow scope and objective activation rules.

## Key Points

- Encode every activation condition on-chain where possible.
- Separate deadlock recovery from ordinary emergency administration.
- Emit detailed events for each recovery action.
- Keep recovery selectors fixed or governance-timelocked.
- Test that the committee cannot act before timeout or outside listed actions.

## Source Evidence

- Lido Dual Governance includes tiebreaker powers gated by prolonged blocked states, including recovery paths around paused exit blockers.

## Related Patterns

- [Exit-Dependent Governance Deadlock](./risk-exit-dependent-governance-deadlock.md)
- [Break-Glass Risk Limiter](../access-control/pattern-break-glass-risk-limiter.md)
