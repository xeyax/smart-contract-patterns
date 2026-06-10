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

## Trade-offs

**Pros:**
- Claim gas is low and independent of recipient count; the bitmap packs 256 claims per storage slot.
- A fixed root with no update machinery keeps the contract small and easy to audit.
- Index-bound leaves make double-claim prevention unambiguous.
- A deadline-gated sweep recovers unclaimed tokens cleanly.

**Cons:**
- The root is immutable: any allocation error means deploying and funding a new distributor.
- Correctness rests entirely on off-chain input validation (duplicates, zero amounts); the contract cannot detect a bad tree.
- No support for recurring or delta rewards — wrong tool for ongoing programs.
- Missing leaf/internal-node domain separation enables forged-proof attacks, especially when trees are reused for other claims.
- Sweep timing is a trust point: sweeping before a fair claim window expropriates slow claimers.

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
- Domain-separate leaf hashes from internal-node hashes, especially when the tree is reused for escrow creation, sale caps, or non-airdrop claims.
- Validate the off-chain input set for duplicate addresses, duplicate indexes, and zero amounts.
- Publish the generated claim blob and token total.
- If unclaimed tokens can be swept, enforce a public deadline or closed state before sweeping.
- For Solana accounts with fixed base state, store processed bits in explicit remaining-data ranges and test that reward, debt, and write-off bitmaps do not overlap.
- Test double claims, wrong address, wrong amount, invalid proof, and post-sweep claims.

## Source Evidence

- SSV uses a fixed Merkle distributor with packed claim bitmap tracking, deterministic off-chain claim generation, and tests for full claims, double claims, and invalid proofs.
- DoubleZero Solana stores processed reward, debt, and debt-write-off bitmaps in distribution `remaining_data` ranges and tests bitmap boundaries in [`programs/revenue-distribution/src/state/distribution.rs`](https://github.com/doublezerofoundation/doublezero-solana/blob/4368da2c446b799f354aecb6156fc0e77343634b/programs/revenue-distribution/src/state/distribution.rs) and `tests/distribute_rewards_test.rs`.
- Jupiter Lock and Meteora Presale both domain-separate Merkle leaves from internal nodes in [`merkle-tree/src/merkle_tree.rs`](https://github.com/jup-ag/jup-lock/blob/f1535b4067b1d90fd682edc94ac693496b0a9812/merkle-tree/src/merkle_tree.rs) and [`merkle-tree/src/tree_node.rs`](https://github.com/MeteoraAg/presale/blob/2acd7c9c20bada425e9ff493260be4328b350b57/merkle-tree/src/tree_node.rs).

## Related Patterns

- [Delayed Cumulative Merkle Claims](./pattern-delayed-cumulative-merkle-claims.md)
- [Queued Reward Streaming](./pattern-queued-reward-streaming.md)
- [Snapshot-Gated Integration Reward Distribution](./pattern-snapshot-gated-integration-reward-distribution.md)
- [Merkle-Instantiated Vesting Escrow Factory](./pattern-merkle-instantiated-vesting-escrow-factory.md)
- [Merkle-Scoped Sale Escrow Caps](../access-control/pattern-merkle-scoped-sale-escrow-caps.md)
