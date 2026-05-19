# Indexed Merkle Airdrop

> Distribute a fixed reward set with an indexed Merkle root and bitmap claim tracking so each allocation can be claimed exactly once.

## Metadata

| Property | Value |
|----------|-------|
| Category | rewards |
| Tags | rewards, merkle, airdrop, bitmap, claim |
| Complexity | Low |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- A fixed off-chain allocation should be claimable on-chain
- The root will not be updated cumulatively over time
- Claim gas should be low and independent of total recipients
- A post-deadline sweep is needed for unclaimed tokens

## Avoid When

- Rewards update periodically and users should claim deltas across roots
- Allocation generation cannot prevent duplicates or zero amounts
- The sweep can happen before users have a fair claim window

## How It Works

The leaf binds index, account, and amount:

```solidity
leaf = keccak256(abi.encodePacked(index, account, amount));
```

The contract tracks claimed indexes in a bitmap:

```solidity
function claim(uint256 index, address account, uint256 amount, bytes32[] calldata proof) external {
    require(!isClaimed(index), "claimed");
    require(MerkleProof.verify(proof, root, leaf(index, account, amount)), "bad proof");
    _setClaimed(index);
    token.transfer(account, amount);
}
```

## Key Points

- Include `index` in the leaf so bitmap tracking is unambiguous.
- Validate the off-chain input set for duplicate addresses, duplicate indexes, and zero amounts.
- Publish the generated claim blob and token total.
- If unclaimed tokens can be swept, enforce a public deadline or closed state before sweeping.
- For Solana accounts with fixed base state, store processed bits in explicit remaining-data ranges and test that reward, debt, and write-off bitmaps do not overlap.
- Test double claims, wrong address, wrong amount, invalid proof, and post-sweep claims.

## Source Evidence

- SSV uses a fixed Merkle distributor with packed claim bitmap tracking, deterministic off-chain claim generation, and tests for full claims, double claims, and invalid proofs.
- DoubleZero Solana stores processed reward, debt, and debt-write-off bitmaps in distribution `remaining_data` ranges and tests bitmap boundaries in `/private/tmp/defillama-source/doublezerofoundation__doublezero-solana/programs/revenue-distribution/src/state/distribution.rs` and `tests/distribute_rewards_test.rs`.

## Related Patterns

- [Delayed Cumulative Merkle Claims](./pattern-delayed-cumulative-merkle-claims.md)
- [Queued Reward Streaming](./pattern-queued-reward-streaming.md)
- [Snapshot-Gated Integration Reward Distribution](./pattern-snapshot-gated-integration-reward-distribution.md)
