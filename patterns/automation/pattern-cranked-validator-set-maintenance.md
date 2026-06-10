# Cranked Validator Set Maintenance

> Maintain large validator sets through an explicit on-chain phase machine with bounded per-validator cranks and epoch gates.

## Metadata

| Property | Value |
|----------|-------|
| Category | automation |
| Platform | solana |
| Tags | automation, solana, validator-set, crank, epoch |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Validator-set maintenance cannot fit in one transaction or instruction
- Maintenance must progress across epochs or phases
- Per-validator work can be made independently crankable
- The protocol can store progress bitmaps or cursors on-chain

## Avoid When

- A single atomic update is required for safety
- Phase transitions cannot tolerate keeper delays
- Validator-list length can change without being reflected in internal accounting
- Progress state can be reset by unauthorized callers

## Trade-offs

**Pros:**
- Handles validator sets far larger than any single transaction's compute or account limits
- Bounded cranks keep each transaction's cost predictable and crankable by any keeper
- Persistent bitmaps and cursors let maintenance resume cleanly after interruption
- Length-vs-accounting checks at phase transitions catch external validator-list drift

**Cons:**
- Liveness depends on keepers cranking; a stalled phase blocks epoch maintenance until someone intervenes
- The epoch/phase/bitmap/pending-count state machine is significant audit surface with many invalid-transition edge cases
- Maintenance spans many transactions, leaving the set in observable intermediate states for long windows
- Progress bitmaps and accounting fields carry ongoing storage cost on-chain
- Recovery procedures for stuck or stale phases must be designed, exposed, and monitored explicitly

## How It Works

Store a maintenance state machine with epoch, phase, and progress:

```rust
enum Phase {
    Idle,
    ComputeScores,
    Rebalance,
    Finalize,
}

struct MaintenanceState {
    epoch: u64,
    phase: Phase,
    progress_bitmap: Vec<u64>,
    validator_count: u32,
    pending_additions: u32,
    pending_removals: u32,
}
```

Each crank verifies the expected phase and processes a bounded validator subset. Phase transitions verify that the external validator list length matches internal accounting plus pending additions or removals.

## Key Points

- Persist epoch, phase, progress, and validator-count accounting.
- Bound each crank by validator count, bitmap range, or max work.
- Gate transitions on current epoch and prior phase completion.
- Verify external validator-list length against internal accounting.
- Monitor stalled phases and expose recovery procedures.
- Test full cycles, partial cranks, wrong phase, stale epoch, and validator-list length mismatch.

## Source Evidence

- Jito StakeNet stores validator maintenance phase and progress state, validates validator-list accounting, gates epoch maintenance, and tests cycle transitions and resets.

## Related Patterns

- [Operation Cadence Liveness Agent](../monitoring/pattern-operation-cadence-liveness-agent.md)
- [Bounded Cranked Orderbook Maintenance](../liquidity/pattern-bounded-cranked-orderbook-maintenance.md)
