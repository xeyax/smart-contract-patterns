# Time-Decaying Lock Voting Escrow

> Mint non-transferable voting power from locked tokens where power decays linearly toward zero as the selected unlock time approaches.

## Metadata

| Property | Value |
|----------|-------|
| Category | governance |
| Tags | governance, voting-escrow, lock, decay, non-transferable |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Governance wants longer explicit lock commitments to receive more voting power
- Voting power should decrease automatically as lock expiry approaches
- Tokenized or transferable voting power would undermine the governance model
- Gauge or reward systems can checkpoint historical voting power

## Avoid When

- Users need liquid governance power or easy delegation through transferable tokens
- The protocol cannot tolerate lock-extension and checkpoint complexity
- On-chain consumers require exact current totals without checkpoint maintenance
- Smart-contract wallet exclusion would harm the intended governance audience

## Trade-offs

**Pros:**
- Aligns voting power with explicit long-term lock commitments
- Voting power naturally decays without a separate unstake transaction
- Historical checkpoints support gauge and fee-distribution accounting

**Cons:**
- Users lose liquidity until lock expiry
- Checkpoint and slope-change accounting is complex
- EOA-only anti-tokenization policies can exclude smart wallets and relayers

## How It Works

Each account chooses an unlock time. Voting power is represented as a slope and
bias, where the bias decays linearly until the lock end:

```solidity
slope = lockedAmount / MAX_LOCK_TIME;
bias = slope * (unlockTime - block.timestamp);

function votingPower(address account) view returns (uint256) {
    Point memory p = userPoint[account];
    uint256 elapsed = block.timestamp - p.timestamp;
    return p.bias > p.slope * elapsed ? p.bias - p.slope * elapsed : 0;
}
```

Checkpointing records user and total-supply points so historical votes and fee
distribution can query past power.

## Key Points

- Round lock ends to a fixed epoch such as weeks to bound checkpoint state.
- Make voting power non-transferable.
- Checkpoint user and total supply changes before deposits, lock extensions, and
  withdrawals.
- Bound maximum lock duration and reject expired-lock voting.
- Be explicit about smart-contract wallet policy; EOA-only checks are governance
  anti-tokenization choices, not general security boundaries.
- Test create-lock, increase amount, extend lock, withdraw after expiry, and
  historical balance queries.

## Source Evidence

- Curve DAO VotingEscrow describes non-transferable time-decaying voting power
  and lock-end-based decay in [`contracts/VotingEscrow.vy:1-10`](https://github.com/curvefi/curve-dao-contracts/blob/fa127b1cb7bf83e4f3d605f7244b7b4ed5ebe053/contracts/VotingEscrow.vy#L1-L10).
- Curve VotingEscrow stores user/global point history and updates locked balances
  through checkpointed create/increase/withdraw paths in [`contracts/VotingEscrow.vy:234-347`](https://github.com/curvefi/curve-dao-contracts/blob/fa127b1cb7bf83e4f3d605f7244b7b4ed5ebe053/contracts/VotingEscrow.vy#L234-L347),
  [`contracts/VotingEscrow.vy:384-488`](https://github.com/curvefi/curve-dao-contracts/blob/fa127b1cb7bf83e4f3d605f7244b7b4ed5ebe053/contracts/VotingEscrow.vy#L384-L488),
  and [`contracts/VotingEscrow.vy:523-660`](https://github.com/curvefi/curve-dao-contracts/blob/fa127b1cb7bf83e4f3d605f7244b7b4ed5ebe053/contracts/VotingEscrow.vy#L523-L660).
- Curve integration tests cover lock and voting-power behavior in
  [`tests/integration/VotingEscrow/test_voting_escrow.py:50-115`](https://github.com/curvefi/curve-dao-contracts/blob/fa127b1cb7bf83e4f3d605f7244b7b4ed5ebe053/tests/integration/VotingEscrow/test_voting_escrow.py#L50-L115).

## Related Patterns

- [Capped Linear Voting Escrow](./pattern-capped-linear-voting-escrow.md)
- [Dynamic-Power Gauge Allocation](./pattern-dynamic-power-gauge-allocation.md)
- [Flash Loan Governance](../../ANTIPATTERNS.md#flash-loan-governance)
