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

## Trade-offs

**Pros:**
- Detects stalled keepers before users hit stuck withdrawals or settlement delays, converting incidents into operational pages.
- Checking state progress and amount ranges catches degraded operation (wrong sizes, stuck queues) that simple call-count monitors miss.
- Read-only and key-isolated: the monitor adds no on-chain attack surface and cannot be turned against the protocol.
- Persisted cursors and packet-state tracking in the cross-chain variant prevent silently skipped work after restarts.

**Cons:**
- Pure off-chain mitigation — it shortens detection time but cannot guarantee solvency or replace on-chain claim reserves.
- Expected cadence, amount ranges, and healthy-idle conditions need per-protocol tuning; poor thresholds yield alert fatigue or missed failures.
- The monitor is its own service with RPC redundancy, state persistence, and uptime requirements — operational burden on top of the keeper fleet it watches.
- Distinguishing healthy idleness from failure is genuinely hard for bursty workloads, leaving a residual false-negative window.
- Alerts are only as good as the response runbook; without defined procedures the agent observes outages without shortening them.

## How It Works

Track the last successful operation and compare it to protocol-specific expectations:

```text
check unstake cadence:
  last_success <= max_interval
  processed_amount within expected range
  queue_head advanced or no pending queue exists
```

The agent should alert on both missing calls and suspiciously small or large amounts.

### Cross-Chain Verifier Worker Variant

For bridge verifier or DVN workers, cadence is not enough. Persist source event cursors, in-flight packet ids, proof request hashes, submitted transaction hashes, retry counts, and final verification or execution status:

```text
PacketSent
  -> proof requested
  -> proof received
  -> verification tx submitted
  -> receive library committed
  -> destination execution observed
```

Starting from the latest block after a restart can silently skip pending packets. Treat worker persistence, redundant RPC, gas funding, and alerting as part of the bridge liveness design.

## Key Points

- Monitor state progress, not only function calls.
- Define healthy idle conditions, such as an empty queue.
- Alert on failed transactions, stale cadence, and suspicious amounts.
- Keep monitors read-only and independent from keeper keys.
- Treat monitor coverage as part of the operational runbook.
- For cross-chain workers, alert on stuck packet states, repeated proof failures, skipped cursors, and already-verified races that do not reach destination execution.
- Monitoring operator top-ups or interest distribution cadence does not replace on-chain claim reserves; it should alert before liveness fails, not define the solvency condition.

## Source Evidence

- Stader BNBx includes off-chain agent checks for operation cadence and suspicious staking or withdrawal amounts around keeper-dependent liquid-staking flows.
- GAIB's Symbiotic Super Sum simulation documents DVN worker state, proof submission, already-verified races, and the need for persistent state, redundant RPC, gas strategy, and monitoring before production use.
- SlowMist's Avalon USDa audit provides a lower-confidence audit-source reminder that keeper or operator funding cadence must be paired with explicit reserve checks for user claims.

## Related Patterns

- [Read-Only Protocol Health Checker](./pattern-read-only-protocol-health-checker.md)
- [Async Deposit/Withdrawal](../vaults/pattern-async-deposit.md)
- [Stake-Backed DVN Verifier Adapter](../cross-chain/pattern-stake-backed-dvn-verifier-adapter.md)
