# Dispute-Windowed Operator Batch Bridge

> Let an operator commit batched bridge transfers, then delay execution behind a dispute window where a crew or guardian can stop a bad batch.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, optimistic, batch, dispute-window, operator |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A bridge is intentionally operator-mediated rather than proof-verified
- Deposits can be batched by range and committed by hash
- Users can tolerate delayed execution for monitoring
- There is a separate role or process that can dispute or pause invalid batches

## Avoid When

- Users expect trustless proof-based bridging
- The operator can also bypass the dispute window
- A dispute pause blocks already-valid exits with no recovery path
- Batch contents cannot be reconstructed by monitors

## Trade-offs

**Pros:**
- Cheaper than per-transfer proof verification
- Gives monitors time to stop malformed batches
- Batch ranges and hashes make operator commitments auditable

**Cons:**
- Operator and dispute roles are explicit trust assumptions
- Liveness depends on operator batching
- Pause/dispute semantics can trap funds if too broad

## How It Works

Users queue deposits. The operator commits a contiguous batch range and hash:

```solidity
function depart(uint256 start, uint256 end, bytes32 batchHash) external onlyOperator {
    batches[nextBatchId] = Batch({
        start: start,
        end: end,
        hash: batchHash,
        executableAt: block.timestamp + disputeDelay,
        disputed: false
    });
}

function disembark(uint256 batchId, Transfer[] calldata transfers) external {
    Batch storage b = batches[batchId];
    require(block.timestamp >= b.executableAt, "delay");
    require(!b.disputed, "disputed");
    require(hash(transfers) == b.hash, "bad batch");
    _execute(transfers);
}
```

Crew, guardians, or governance can dispute during the delay.

## Implementation

```solidity
function disputeBatch(uint256 id) external onlyCrew {
    batches[id].disputed = true;
    _pauseBridge();
}
```

### Key Points

- Bind batch hash to domain, token, chain, range, recipients, and amounts.
- Make batch ordering and start/end indexes deterministic.
- Let anyone verify a committed batch from public queue data.
- Keep recovery and jettison semantics explicit when a batch is disputed.
- Bond proposers or data workers when failed execution would otherwise leave monitors with only social recourse.
- If the bridge has a fast-liquidity path, make slow-fill or canonical-fill fallback explicit and consume the same relay id when either path succeeds.
- Document operator custody and admin powers; this is not a trustless bridge.

## Source Evidence

- Fraxferry v1 queues deposits, commits batch hashes/ranges in `depart`, delays execution in `disembark`, and lets crew dispute batches in `/private/tmp/defillama-source/FraxFinance__frax-solidity/src/hardhat/contracts/Fraxferry/Fraxferry.sol`.
- Fraxferry tests cover embark, depart ordering, delayed execution, wrong hash/size/start reverts, jettison, dispute, and pause in `/private/tmp/defillama-source/FraxFinance__frax-solidity/src/hardhat/test/Fraxferry`.
- Across HubPool proposes bonded root bundles containing pool rebalance, relayer refund, and slow-relay roots, waits through liveness, verifies Merkle leaves, and publishes roots to spoke pools in `/private/tmp/defillama-source/across-protocol__contracts/contracts/hub-pool/HubPool.sol`.
- Across SpokePool lets users request slow fills, proves slow-fill leaves against a published root, and marks the same relay filled when either slow or fast fill executes in `/private/tmp/defillama-source/across-protocol__contracts/contracts/spoke-pools/SpokePool.sol`.
- Hop L1 bridge documents bonded transfer-root preconfirmation followed by canonical confirmation from the origin L2 bridge in `/private/tmp/defillama-source/hop-protocol__contracts/contracts/bridges/L1_Bridge.sol`.
- Connext RootManager proposes aggregate roots, supports watcher/dispute-mode controls, and tests optimistic-mode and slow-mode transitions in `/private/tmp/defillama-source/connext__monorepo/packages/deployments/contracts/contracts/messaging/RootManager.sol` and `contracts_forge/messaging/RootManager.t.sol`.

## Real-World Examples

- Fraxferry v1 - optimistic operator batch bridge with delayed disembark and crew dispute.
- Across V3 - bonded root bundles publish refund and slow-fill roots after liveness.
- Connext - aggregate root settlement combines optimistic root proposals with watcher-mediated slow mode.

## Related Patterns

- [Chain-Bound Request Hash](./pattern-chain-bound-request-hash.md)
- [Fraud-Window Gated Message Finality](./pattern-fraud-window-gated-message-finality.md)
- [Threshold-Delayed Bridge Payout](./pattern-threshold-delayed-bridge-payout.md)
- [Pause Traps Funds](../../ANTIPATTERNS.md#pause-traps-funds)

## References

- See Source Evidence.
