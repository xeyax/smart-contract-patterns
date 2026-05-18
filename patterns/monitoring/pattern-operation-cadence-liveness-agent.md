# Operation Cadence Liveness Agent

> Monitor keeper-dependent operations against expected cadence, amounts, and state movement so delayed maintenance is detected before users are stuck.

## Metadata

| Property | Value |
|----------|-------|
| Category | monitoring |
| Tags | monitoring, keeper, liveness, cadence, operations |
| Complexity | Medium |
| Gas Efficiency | N/A |
| Audit Risk | Low |

## Use When

- Protocol liveness depends on bots, keepers, or operators
- Missing operations can delay withdrawals, settlement, rewards, or staking maintenance
- Amounts or state changes can be checked from public events or views
- Operators need alerting before the issue becomes user-facing

## Avoid When

- The operation is fully user-driven and has no expected cadence
- Missing an operation has no protocol or user impact
- The monitor cannot distinguish healthy idleness from failure
- Alert response procedures are undefined

## How It Works

Track the last successful operation and compare it to protocol-specific expectations:

```text
check unstake cadence:
  last_success <= max_interval
  processed_amount within expected range
  queue_head advanced or no pending queue exists
```

The agent should alert on both missing calls and suspiciously small or large amounts.

## Key Points

- Monitor state progress, not only function calls.
- Define healthy idle conditions, such as an empty queue.
- Alert on failed transactions, stale cadence, and suspicious amounts.
- Keep monitors read-only and independent from keeper keys.
- Treat monitor coverage as part of the operational runbook.

## Source Evidence

- Stader BNBx includes off-chain agent checks for operation cadence and suspicious staking or withdrawal amounts around keeper-dependent liquid-staking flows.

## Related Patterns

- [Read-Only Protocol Health Checker](./pattern-read-only-protocol-health-checker.md)
- [Async Deposit/Withdrawal](../vaults/pattern-async-deposit.md)
