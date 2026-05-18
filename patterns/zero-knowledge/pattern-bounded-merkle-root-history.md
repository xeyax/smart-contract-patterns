# Bounded Merkle Root History

> Keep a fixed-size ring of recent Merkle roots so asynchronous zk proofs can verify membership without accepting unbounded stale state.

## Metadata

| Property | Value |
|----------|-------|
| Category | zero-knowledge |
| Tags | zk, merkle-tree, root-history, ring-buffer |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- Users generate proofs against roots that may be a few blocks old
- The contract appends leaves and publishes new roots over time
- Proof generation latency must be tolerated
- Very old roots should expire automatically

## Avoid When

- Proofs must remain valid indefinitely
- Root history length cannot cover expected proof latency
- The tree update path can skip or overwrite roots unpredictably
- A full light-client history is required instead of a local tree history

## How It Works

Store each new root in a fixed ring and accept membership proofs only for roots still in the ring:

```solidity
function _insert(bytes32 leaf) internal {
    bytes32 newRoot = _appendLeaf(leaf);
    currentRootIndex = (currentRootIndex + 1) % ROOT_HISTORY_SIZE;
    roots[currentRootIndex] = newRoot;
}

function isKnownRoot(bytes32 root) public view returns (bool) {
    for (uint256 i; i < ROOT_HISTORY_SIZE; i++) {
        if (roots[i] == root) return true;
    }
    return false;
}
```

The root window is an availability parameter: shorter windows reduce stale-root exposure but increase proof-latency failures.

## Key Points

- Initialize the tree with a valid empty root.
- Reject zero or unknown roots.
- Test ring wraparound and expiry boundaries.
- Size the window for realistic proof generation, relayer delay, and chain congestion.
- Keep nullifier uniqueness separate from root membership.

## Source Evidence

- Tornado Nova's Merkle tree keeps a bounded root history and tests recent root acceptance, old-root expiry, and ring-buffer wrap behavior.

## Related Patterns

- [Shielded Pool Accounting Invariants](./req-shielded-pool-accounting-invariants.md)
- [Checkpointed Receipt Exit Proof](../cross-chain/pattern-checkpointed-receipt-exit-proof.md)
