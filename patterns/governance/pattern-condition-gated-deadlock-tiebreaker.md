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

## Trade-offs

**Pros:**
- Objective on-chain conditions plus timeouts stop the committee from acting outside genuine deadlock.
- Narrowly enumerated recovery selectors bound worst-case committee abuse to resume/reseal actions.
- Restores liveness without granting anyone standing emergency power over normal governance.
- Detailed per-action events make every recovery publicly attributable and reviewable.

**Cons:**
- The committee remains a trust assumption; collusion after an engineered deadlock can still exercise recovery powers.
- Encoding deadlock objectively is hard — loose conditions enable premature activation, strict ones may never fire when actually needed.
- The mandatory timeout delays recovery even when the deadlock is obvious, prolonging the liveness failure.
- It is a rarely exercised code path: bugs lie dormant until the worst moment, demanding heavy scenario and negative testing.
- The recovery selector list needs governance-timelocked maintenance as the system evolves, or new modules remain unrecoverable.

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
