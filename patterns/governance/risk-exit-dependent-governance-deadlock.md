# Exit-Dependent Governance Deadlock

> Governance can become blocked waiting for users to exit while the exit path itself depends on paused, delayed, or governance-controlled components.

## Metadata

| Property | Value |
|----------|-------|
| Category | governance |
| Tags | governance, deadlock, exit, pause, liveness |
| Type | Risk Description |

## Applies When

- Veto, rage-quit, or emergency governance depends on users exiting before proposals proceed
- Exit processing depends on withdrawal queues, oracles, bridges, keepers, or pause controls
- The same governance domain controls components needed to unblock the exit
- There is no objective timeout or tiebreaker

## Requirements Affected

- Veto systems must preserve exit liveness and proposal liveness at the same time.
- Emergency pauses must not silently disable the only path out of a governance dispute.

## Failure Modes

- Proposal execution is blocked until exits complete, but exits cannot complete while an oracle or queue is paused.
- A committee cannot resume the exit dependency because normal governance is already blocked.
- Users cannot tell whether waiting, claiming, or cancelling is the safe path.

## Mitigations

- Keep the safest solvent exit path open during governance disputes.
- Add bounded public processing and timeout-based recovery.
- Separate pause permissions for proposal flow and exit dependencies.
- Document dependencies on oracle updates, bridge finality, and withdrawal queues.

## Source Evidence

- Lido Dual Governance includes explicit deadlock and tiebreaker handling because proposal liveness can depend on staking-withdrawal exit progress.

## Related Patterns

- [Veto Governance Liveness And Exit Safety Requirements](./req-veto-governance-liveness-and-exit-safety.md)
- [Condition-Gated Deadlock Tiebreaker](./pattern-condition-gated-deadlock-tiebreaker.md)
- [Pause Traps Funds](../../ANTIPATTERNS.md#pause-traps-funds)
