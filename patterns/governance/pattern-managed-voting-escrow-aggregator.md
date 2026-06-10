# Managed Voting-Escrow Aggregator

> Aggregate user voting-escrow locks into managed veNFT positions that coordinate deposits, withdrawals, rewards, and gauge voting as one managed entity.

## Metadata

| Property | Value |
|----------|-------|
| Category | governance |
| Tags | governance, voting-escrow, venft, managed-lock, gauge |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Voting escrow positions are tokenized as NFTs or transferable lock records
- Users want to delegate locked liquidity into a managed strategy or gauge allocator
- Managed positions need separate reward accounting and deposit/withdraw rules
- Same-block or flash deposit behavior would distort gauge voting or reward claims

## Avoid When

- Voting power must remain strictly non-transferable per user
- Managed lock operators can redirect user principal without objective withdrawal rules
- Gauge voting cannot distinguish managed and ordinary locks
- The protocol cannot test deposit, withdrawal, and reward timing around block boundaries

## Trade-offs

**Pros:**
- Lets many users coordinate gauge voting through a single managed lock
- Separates managed-lock rewards from ordinary veNFT rewards
- Can support strategy-like voting products without minting liquid voting power

**Cons:**
- Increases trust and accounting complexity around the manager
- Deposit and withdrawal paths can affect gauge voting state
- Same-block protections and managed-state transitions are easy to miss

## How It Works

A managed lock is a special voting-escrow NFT. Users deposit ordinary locks into
the managed position and receive an account-level record or claim on the managed
state:

```solidity
function depositManaged(uint256 tokenId, uint256 managedTokenId) external {
    _checkpoint(tokenId);
    _checkpoint(managedTokenId);
    _transferVotingPower(tokenId, managedTokenId);
    managedDeposits[tokenId] = managedTokenId;
}
```

Withdrawals reverse the relationship and refresh voting state before the user
can act independently:

```solidity
function withdrawManaged(uint256 tokenId) external {
    uint256 managedTokenId = managedDeposits[tokenId];
    _checkpoint(managedTokenId);
    delete managedDeposits[tokenId];
    _restoreVotingPower(tokenId, managedTokenId);
}
```

The voter or gauge controller must treat managed deposit and withdrawal as
voting-state changes, not as ordinary NFT transfers.

## Implementation

### Key Points

- Separate managed lock state from ordinary lock ownership and voting power.
- Checkpoint both the user lock and managed lock before deposits or withdrawals.
- Prevent same-block deposit, vote, withdraw, or reward-claim shortcuts that reuse voting power.
- Define who can create, activate, deactivate, or permanently lock a managed position.
- Route managed rewards through explicit reward contracts or indexes.
- Test flash deposit/withdraw behavior, gauge revotes, reward claims, manager deactivation, and user exit.

## Source Evidence

- Aerodrome creates managed locks, deposits user positions into managed NFTs, and handles withdrawal state in [`contracts/VotingEscrow.sol`](https://github.com/aerodrome-finance/contracts/blob/1ba30815bba620f7e9faa34769ffd00c214c9b82/contracts/VotingEscrow.sol).
- Aerodrome `Voter` wires managed deposit and withdrawal into voting state in [`contracts/Voter.sol`](https://github.com/aerodrome-finance/contracts/blob/1ba30815bba620f7e9faa34769ffd00c214c9b82/contracts/Voter.sol).
- Aerodrome tests cover managed NFT behavior and same-block protections in [`test/ManagedNft.t.sol`](https://github.com/aerodrome-finance/contracts/blob/1ba30815bba620f7e9faa34769ffd00c214c9b82/test/ManagedNft.t.sol).

## Real-World Examples

- Aerodrome - managed veNFTs aggregate locked voting escrow positions and coordinate gauge voting.

## Related Patterns

- [Time-Decaying Lock Voting Escrow](./pattern-time-decaying-lock-voting-escrow.md)
- [Dynamic-Power Gauge Allocation](./pattern-dynamic-power-gauge-allocation.md)
- [Flash Loan Governance](../../ANTIPATTERNS.md#flash-loan-governance)

## References

- See Source Evidence.
