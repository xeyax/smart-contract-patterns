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

- zkSync Era gateway messaging docs in `/private/tmp/defillama-source/matter-labs__zksync-era/docs/src/specs/contracts/gateway/l2_gw_l1_messaging.md` describe domain-scoped message roots and unique message ids; integration tests in `core/tests/ts-integration/tests/interop-a.test.ts` cover interop message behavior.
- Linea accumulates ordered rolling hashes and sparse Merkle roots in `/private/tmp/defillama-source/Consensys__linea-monorepo/contracts/src/messaging/l1/L1MessageService.sol` and `L1MessageManager.sol`, with claim tests in `contracts/test/hardhat/messaging/l1/L1MessageService.ts`.
- Agglayer combines domain exit roots in `/private/tmp/defillama-source/agglayer__agglayer-contracts/contracts/AgglayerGER.sol` using `contracts/lib/GlobalExitRootLib.sol`.
- Agglayer bridge claims set nullifiers before callbacks in `AgglayerBridge.sol`, with reentrancy tests in `BridgeV2ClaimMessageReentrancy.test.ts`.
- Polygon zkEVM/Agglayer contracts update mainnet and rollup exit roots, compute global exit roots, and prove claims against root histories in `/private/tmp/defillama-source/0xPolygonHermez__zkevm-contracts/contracts/AgglayerGER.sol` and `contracts/AgglayerBridge.sol`.
- Connext aggregates spoke-domain message roots into proposed aggregate roots, uses optimistic/watcher-controlled modes, and proves two-level message inclusion in `/private/tmp/defillama-source/connext__monorepo/packages/deployments/contracts/contracts/messaging/RootManager.sol`, `SpokeConnector.sol`, and `MerkleTreeManager.sol`.
- Socket packs messages into capacitor packet roots, records packet roots by switchboard proposal count, and verifies inclusion before plug execution in `/private/tmp/defillama-source/SocketDotTech__socket-DL/contracts/socket/SocketSrc.sol`, `SocketDst.sol`, and `contracts/capacitors`.

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
