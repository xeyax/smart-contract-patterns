# Proof Bridge Exit Safety Requirements

> Requirements for bridges that release or mint assets from source-chain exit proofs.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, exit, proof, finality, nullifier |
| Type | Requirement |

## R1: Source Proof Is Finalized

**Exit proofs must be accepted only after the source block or message is finalized by the destination chain's trust model.**

### What This Means

- A checkpoint, rollup outbox, or canonical messenger supplies source-domain finality.
- The proof cannot be replayed from an unfinalized or reorged source block.
- Tests cover invalid roots and source blocks outside the accepted finality window.

## R2: Exit Nullifier Is Unique And Normalized

**Each source event or message can be consumed once, even if the same proof has multiple equivalent encodings.**

### What This Means

- The nullifier binds source transaction or message id, log location, and event domain.
- Ambiguous proof encodings are normalized before hashing.
- Duplicate finalization fails before custody changes.

## R3: Emitter And Event Are Authenticated

**The proven source log or message must come from the configured peer and expected event signature.**

### What This Means

- A valid receipt from the wrong child token, tunnel, or gateway is rejected.
- The destination contract verifies event signature, source token, and peer mapping.
- Generic proof dispatch cannot call arbitrary token finalizers.

## R4: Custody Is Sufficient Before Release

**The destination-side finalizer must prove that token-specific custody or mint authority can satisfy the exit.**

### What This Means

- Lock/release predicates hold enough locked root assets.
- Burn/mint bridges retain mint authority until all pending exits are handled.
- Fee-on-transfer or rebasing assets are accounted by balance deltas or rejected.

## R5: Migration Cutovers Preserve Pending Exits

**Bridge migration must not disable valid exits or move custody before a documented final source boundary.**

### What This Means

- The old bridge accepts exits up to a final accepted source block/message boundary, or publishes a replacement claim path.
- Custody migration excludes amounts needed for pending valid exits.
- Cutover state is tested for old exits, new exits, and duplicate exits.

## Source Evidence

- Polygon PoS portal verifies receipt inclusion, checkpoint membership, log emitter mapping, and duplicate-exit nullifiers before dispatch.
- Polygon withdraw tests cover invalid proof and duplicate-exit rejection.
- Migration paths in Polygon predicates illustrate the need to preserve exit boundaries before moving custody.

## Related Patterns

- [Checkpointed Receipt Exit Proof](./pattern-checkpointed-receipt-exit-proof.md)
- [Bridge Exit Liveness Requirements](./req-bridge-exit-liveness.md)
- [Bridge Exit Cutover Custody Drain](./risk-bridge-exit-cutover-custody-drain.md)
