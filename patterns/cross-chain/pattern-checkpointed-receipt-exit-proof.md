# Checkpointed Receipt Exit Proof

> Finalize exits by proving a source-chain receipt log inside a finalized checkpoint before releasing or minting destination assets.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, checkpoint, exit, receipt-proof, merkle-patricia |
| Complexity | High |
| Gas Efficiency | Low |
| Audit Risk | High |

## Use When

- Users exit from a child chain or rollup by proving a burn or message event
- A checkpoint manager publishes finalized source block roots
- The destination chain can verify receipt inclusion and event log extraction
- Exit finalization must be permissionless after finality

## Avoid When

- The source chain has no verifiable finalized checkpoint on the destination chain
- Receipt/log formats are unstable or not parseable on-chain
- A canonical bridge already exposes a safer finalized message primitive

## Trade-offs

**Pros:**
- Lets anyone finalize valid exits after checkpoint finality
- Avoids trusting an off-chain relayer to choose which exits are valid
- Binds release/mint behavior to a concrete source transaction log

**Cons:**
- Proof parsing is complex and chain-format sensitive
- Finality delay can create poor exit UX
- A malformed proof normalizer can create replay or censorship edge cases

## How It Works

The exit function verifies the source receipt in layers:

1. Decode the exit payload and source receipt proof.
2. Verify the receipt exists in the source block receipt root.
3. Verify the source block is included in a finalized checkpoint.
4. Extract the expected event log.
5. Mark the normalized exit nullifier spent.
6. Dispatch the proven event to the token-specific finalizer.

```solidity
function exit(bytes calldata proof) external {
    ExitLog memory log = _verifyCheckpointedReceipt(proof);
    bytes32 nullifier = _exitNullifier(log);

    require(!spent[nullifier], "already exited");
    spent[nullifier] = true;

    _finalizeExit(log);
}
```

## Key Points

- Authenticate the checkpoint manager and source chain domain.
- Normalize proof encodings before hashing nullifiers so equivalent proofs cannot replay.
- Authenticate the log emitter and event signature before dispatch.
- Separate proof validation from token-specific custody logic.
- Test invalid root, invalid receipt, wrong emitter, wrong event, and duplicate-exit cases.

## Source Evidence

- Polygon PoS portal `RootChainManager.exit` verifies child receipt proofs and checkpoint membership before dispatching exits.
- Polygon's Merkle Patricia proof and Merkle membership libraries are tested with invalid proof cases.
- Withdraw tests cover duplicate exit rejection and invalid proof rejection.

## Related Patterns

- [Proof Bridge Exit Safety Requirements](./req-proof-bridge-exit-safety.md)
- [Predicate-Mediated Bridge Custody](./pattern-predicate-mediated-bridge-custody.md)
- [Chain-Bound Request Hash](./pattern-chain-bound-request-hash.md)
