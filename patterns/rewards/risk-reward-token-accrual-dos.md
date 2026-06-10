# Reward Token Accrual DoS

> External reward-token accounting can block deposits, withdrawals, and claims when every user action loops over a bad or extreme reward token.

## Metadata

| Property | Value |
|----------|-------|
| Category | rewards |
| Tags | rewards, dos, external-token, accrual, exit |
| Type | Risk Description |

## Applies When

- Deposit, withdraw, transfer, or claim updates all registered reward tokens
- Reward token registration is owner-curated or governance-curated
- Reward tokens can revert, behave non-standardly, or create expensive accounting
- Users have no principal-only emergency exit path

## Requirements Affected

- Principal exits should not depend on every optional reward token remaining healthy.
- Reward-token registration is a protocol-critical trust boundary.

## Failure Modes

- A reward token reverts during `transfer` or balance reads, blocking normal withdrawals.
- Too many reward tokens make every account action too expensive.
- A misconfigured instant or extreme reward rate causes accrual math to revert.
- Long inactivity makes epoch catch-up loops too expensive for claim or checkpoint transactions.
- Removing a bad reward token forfeits or strands accrued rewards without documentation.

## Mitigations

- Curate reward tokens with token-behavior checks and maximum count limits.
- Keep a principal-only emergency exit path that can skip broken rewards.
- Allow governance to disable or remove a bad reward token with clear forfeiture semantics.
- Bound per-action reward loops or split reward updates into paginated claims.
- Cap epoch catch-up work with cursors, public keeper maintenance, or partial claims.
- Document that optional rewards are junior to principal exit liveness.

## Source Evidence

- Reserve staking contracts and audit material show multi-reward vaults where deposits, withdrawals, and claims update registered external reward tokens, motivating emergency principal-only exits and owner controls for bad rewards.
- Pendle V2 updates reward state during token transfer and claim flows across curated reward tokens, making reward-token list quality a liveness boundary in [`contracts/core/RewardManager`](https://github.com/pendle-finance/pendle-core-v2-public/blob/fdcfe39ed7b45717f0e6e286581bdcf96bb2f9ce/contracts/core/RewardManager).
- Velodrome V2 reward accounting shows epoch-bucketed catch-up loops in [`contracts/Reward.sol`](https://github.com/velodrome-finance/contracts/blob/b3065d8b6702b14b094f9f6046b752cc9f78c43b/contracts/Reward.sol), including a bounded global checkpoint path and claim-time scans over missed epochs.

## Related Patterns

- [Lazy Reward Index](./pattern-lazy-reward-index.md)
- [Queued Reward Streaming](./pattern-queued-reward-streaming.md)
- [Pause Traps Funds](../../ANTIPATTERNS.md#pause-traps-funds)
