# Snapshot-Gated Integration Reward Distribution

> Distribute rewards only after integration state, debt state, and processed bitmaps are finalized for the same distribution snapshot.

## Metadata

| Property | Value |
|----------|-------|
| Category | rewards |
| Platform | solana |
| Tags | rewards, snapshot, bitmap, debt, solana |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Rewards depend on off-chain or cross-program accounting snapshots
- The distribution must account for unpaid debt or bad-debt write-offs
- Claims are proven by indexed leaves and tracked by bitmaps
- Multiple processing phases must happen against the same snapshot

## Avoid When

- Rewards can be streamed continuously without snapshot finalization
- The debt or eligibility set can change while users are claiming
- The protocol cannot bind processed bitmaps to the distribution's configured counts
- Operators can sweep funds before debt/write-off windows complete

## Trade-offs

**Pros:**
- Keeps reward, debt, and write-off state tied to one distribution
- Prevents double processing with compact bitmaps
- Makes cross-phase accounting auditable after the distribution ends

**Cons:**
- More state-machine steps than a basic Merkle airdrop
- Delayed rewards while debt and write-off windows finalize
- Requires careful sizing of account data and bitmap ranges

## How It Works

Initialize a distribution with immutable counts, roots, and processing windows:

```rust
distribution.total_rewards = total_rewards;
distribution.reward_root = reward_root;
distribution.debt_root = debt_root;
distribution.remaining_data = vec![0; bitmap_bytes];
```

Each phase consumes an indexed leaf and marks the corresponding bit in the distribution's remaining data:

```rust
process_leaf_index(
    &mut distribution.remaining_data[processed_bitmap_range],
    leaf_index,
)?;
```

Reward distribution checks that debt finalization and write-off gates are in the correct state before paying or sweeping. Bad debt can be written off in the same distribution only after the distribution permits that phase and before sweep finality.

## Implementation

### Key Points

- Bind every bitmap range to the distribution's configured counts.
- Use separate bitmaps for reward claims, debt payments, and debt write-offs.
- Finalize debt calculation before reward distribution or write-off processing depends on it.
- Prevent sweep while same-distribution write-off or claim windows are still open.
- Test repeated processing, out-of-range indexes, wrong roots, unfinalized debt, and same-distribution write-off paths.

## Source Evidence

- DoubleZero Solana initializes distributions in `try_initialize_distribution`, tracks reward and debt processing in `remaining_data`, and derives disjoint bitmap ranges in [`programs/revenue-distribution/src/processor.rs`](https://github.com/doublezerofoundation/doublezero-solana/blob/4368da2c446b799f354aecb6156fc0e77343634b/programs/revenue-distribution/src/processor.rs) and `src/state/distribution.rs`.
- `try_distribute_rewards`, `try_collect_integration_rewards`, and the Solana validator debt processors mark indexed leaves through `try_process_remaining_data_leaf_index`.
- DoubleZero tests verify reward, debt, and write-off bitmap ranges and same-distribution debt write-off behavior in [`programs/revenue-distribution/tests/distribute_rewards_test.rs`](https://github.com/doublezerofoundation/doublezero-solana/blob/4368da2c446b799f354aecb6156fc0e77343634b/programs/revenue-distribution/tests/distribute_rewards_test.rs) and `write_off_solana_validator_debt_test.rs`.

## Real-World Examples

- DoubleZero Solana revenue distribution - snapshot-gated integration rewards with debt and write-off bitmap accounting.

## Related Patterns

- [Indexed Merkle Airdrop](./pattern-indexed-merkle-airdrop.md)
- [Checkpointed Epoch Reward Buckets](./pattern-checkpointed-epoch-reward-buckets.md)
- [Explicit Bad-Debt Realization](../lending/pattern-explicit-bad-debt-realization.md)

## References

- See Source Evidence.
