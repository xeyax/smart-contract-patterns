# Domain-Scoped Message Root Accumulator

> Accumulate cross-chain message roots by domain and checkpoint combined roots for replay-safe inclusion proofs.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, merkle-root, accumulator, nullifier, checkpoint |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Messages are batched into roots before being proven on another domain
- Multiple domains or chains contribute roots to a shared bridge state
- Claims need exact-once nullifiers even when proof paths differ
- The bridge needs a durable root history for delayed exits

## Avoid When

- Each message is verified directly by a light client without batch roots
- Root writers are unauthenticated or can overwrite history silently
- Equivalent proof encodings can claim the same message through different ids

## Trade-offs

**Pros:**
- Compresses many messages into checkpointed roots
- Separates domain-local root production from global root publication
- Supports delayed inclusion proofs and exact-once claims

**Cons:**
- Root writer governance and finality assumptions are critical
- Nullifier design must survive multiple proof paths
- Root history and batch metadata add operational complexity

## How It Works

Each domain accumulates local messages into a local root. A bridge or aggregator
combines local roots into a checkpointed global root with metadata. Claims prove
message inclusion against the accepted root and consume a stable nullifier before
external effects.

```solidity
function updateExitRoot(uint32 domain, bytes32 localRoot) external onlyRootWriter {
    domainRoots[domain] = localRoot;
    bytes32 globalRoot = hashDomainRoots(domainRoots);
    rootHistory[globalRoot] = RootMetadata({
        domain: domain,
        timestamp: uint64(block.timestamp),
        blockNumber: uint64(block.number)
    });
    emit GlobalRootUpdated(globalRoot);
}

function claim(Message calldata message, Proof calldata proof) external {
    bytes32 nullifier = message.nullifier();
    require(!claimed[nullifier], "claimed");
    require(_verifyInclusion(message, proof), "bad proof");
    claimed[nullifier] = true;
    _deliver(message);
}
```

## Implementation

- Domain-separate chain id, batch id, local root, global root, and message id.
- Authenticate root writers and emit enough metadata for monitors.
- Keep root history long enough for expected exit windows.
- Normalize equivalent proof paths into one nullifier.
- Set nullifiers before external callbacks or token transfers.
- Test duplicate claims through alternate proof paths, stale roots, wrong domains, and callback reentrancy.
- When a packet root combines route-specific message ids, bind the source chain, sibling sender, destination chain, local receiver, and execution params before proving inclusion.
- For optimistic aggregate roots, document who can propose, who can dispute, and whether switching modes discards queued roots.

## Source Evidence

- zkSync Era gateway messaging docs in [`docs/src/specs/contracts/gateway/l2_gw_l1_messaging.md`](https://github.com/matter-labs/zksync-era/blob/3f99eb0d62eb7dba159b78b7e842b9c73f5cf3d0/docs/src/specs/contracts/gateway/l2_gw_l1_messaging.md) describe domain-scoped message roots and unique message ids; integration tests in `core/tests/ts-integration/tests/interop-a.test.ts` cover interop message behavior.
- Linea accumulates ordered rolling hashes and sparse Merkle roots in [`contracts/src/messaging/l1/L1MessageService.sol`](https://github.com/Consensys/linea-monorepo/blob/1f6880839cd2dff45009ccd9bffef0e68b0bb2f3/contracts/src/messaging/l1/L1MessageService.sol) and `L1MessageManager.sol`, with claim tests in `contracts/test/hardhat/messaging/l1/L1MessageService.ts`.
- Agglayer combines domain exit roots in [`contracts/AgglayerGER.sol`](https://github.com/agglayer/agglayer-contracts/blob/110bda5a03e70ee7331bc06407a8e79226d3e520/contracts/AgglayerGER.sol) using `contracts/lib/GlobalExitRootLib.sol`.
- Agglayer bridge claims set nullifiers before callbacks in `AgglayerBridge.sol`, with reentrancy tests in `BridgeV2ClaimMessageReentrancy.test.ts`.
- Polygon zkEVM/Agglayer contracts update mainnet and rollup exit roots, compute global exit roots, and prove claims against root histories in [`contracts/AgglayerGER.sol`](https://github.com/0xPolygonHermez/zkevm-contracts/blob/110bda5a03e70ee7331bc06407a8e79226d3e520/contracts/AgglayerGER.sol) and `contracts/AgglayerBridge.sol`.
- Connext aggregates spoke-domain message roots into proposed aggregate roots, uses optimistic/watcher-controlled modes, and proves two-level message inclusion in [`packages/deployments/contracts/contracts/messaging/RootManager.sol`](https://github.com/connext/monorepo/blob/7758e62037bba281b8844c37831bde0b838edd36/packages/deployments/contracts/contracts/messaging/RootManager.sol), `SpokeConnector.sol`, and `MerkleTreeManager.sol`.
- Socket packs messages into capacitor packet roots, records packet roots by switchboard proposal count, and verifies inclusion before plug execution in [`contracts/socket/SocketSrc.sol`](https://github.com/SocketDotTech/socket-DL/blob/b2601e280533960df4d36eeef25ab81957f59eb9/contracts/socket/SocketSrc.sol), `SocketDst.sol`, and `contracts/capacitors`.

## Real-World Examples

- zkSync Era, Linea, and Agglayer use root-based message or exit proof flows with domain separation and exact-once claim semantics.

## Related Patterns

- [Checkpointed Receipt Exit Proof](./pattern-checkpointed-receipt-exit-proof.md)
- [Bounded Merkle Root History](../zero-knowledge/pattern-bounded-merkle-root-history.md)
- [Retryable Cross-Domain Message Ledger](./pattern-retryable-cross-domain-message-ledger.md)
- [Dispute-Windowed Operator Batch Bridge](./pattern-dispute-windowed-operator-batch-bridge.md)

## References

- zkSync Era gateway messaging docs.
- Linea message service contracts.
- Agglayer global exit root contracts.
