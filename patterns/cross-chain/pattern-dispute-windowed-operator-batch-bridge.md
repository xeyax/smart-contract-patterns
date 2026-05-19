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
- Document operator custody and admin powers; this is not a trustless bridge.

## Source Evidence

- Fraxferry v1 queues deposits, commits batch hashes/ranges in `depart`, delays execution in `disembark`, and lets crew dispute batches in `/private/tmp/defillama-source/FraxFinance__frax-solidity/src/hardhat/contracts/Fraxferry/Fraxferry.sol`.
- Fraxferry tests cover embark, depart ordering, delayed execution, wrong hash/size/start reverts, jettison, dispute, and pause in `/private/tmp/defillama-source/FraxFinance__frax-solidity/src/hardhat/test/Fraxferry`.

## Real-World Examples

- Fraxferry v1 - optimistic operator batch bridge with delayed disembark and crew dispute.

## Related Patterns

- [Chain-Bound Request Hash](./pattern-chain-bound-request-hash.md)
- [Fraud-Window Gated Message Finality](./pattern-fraud-window-gated-message-finality.md)
- [Pause Traps Funds](../../ANTIPATTERNS.md#pause-traps-funds)

## References

- See Source Evidence.
