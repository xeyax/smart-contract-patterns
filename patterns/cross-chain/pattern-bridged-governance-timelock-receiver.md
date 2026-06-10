# Bridged Governance Timelock Receiver

> Receive governance messages from a canonical bridge, validate the root timelock sender, and queue actions into a local timelock before execution.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | governance, bridge, timelock, receiver, cross-chain |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Root governance lives on one chain and controls deployments on another
- The destination chain has a local timelock or delay requirement
- Canonical bridge sender/origin can be authenticated
- Governance actions may contain multiple target/calldata entries

## Avoid When

- Bridge messages cannot authenticate both messenger and root sender
- Destination execution must happen immediately without local review
- The receiver can execute arbitrary calldata without queueing or expiry

## Trade-offs

**Pros:**
- Local timelock gives destination-chain operators and users a review and exit window before root governance actions execute.
- Dual authentication of canonical messenger and root sender blocks spoofed proposals from arbitrary bridge callers.
- Hashing full proposal contents into the queued id prevents queue/execute mismatches and duplicate execution.
- Expiry rules clear stale proposals instead of leaving an indefinitely executable backlog.

**Cons:**
- Two stacked timelocks (root plus local) compound governance latency; urgent fixes on the destination chain are slow.
- The receiver is arbitrary-execution infrastructure: one authentication bug compromises every contract it governs.
- All cross-chain governance depends on canonical bridge liveness; a bridge pause or dropped message stalls upgrades and parameter changes.
- Each chain's messenger has different authentication semantics, so the receiver needs bespoke per-chain auth code, multiplying audit surface.

## How It Works

The receiver validates the bridge context, decodes the proposal batch, and queues it locally:

```solidity
function receiveMessage(bytes calldata data) external onlyCanonicalMessenger {
    require(rootSender() == rootTimelock, "bad root sender");
    Proposal memory proposal = abi.decode(data, (Proposal));
    bytes32 id = hashProposal(proposal);
    localTimelock.queue(id, proposal.targets, proposal.values, proposal.calldatas);
}

function execute(bytes32 id) external {
    require(localTimelock.ready(id), "not ready");
    localTimelock.execute(id);
}
```

## Key Points

- Validate canonical messenger and original root governance sender.
- Hash targets, values, signatures, calldatas, and salt/nonces into the local queued id.
- Reject duplicate, malformed, expired, or unqueued proposals.
- Keep local timelock delay and expiry visible to operators.
- Treat the receiver as arbitrary execution infrastructure and monitor it accordingly.

## Source Evidence

- Compound III bridge receivers authenticate chain-specific canonical messengers and root timelock senders, queue decoded proposal batches into local timelocks, and test unauthorized sender, duplicate transaction, expiry, queueing, and execution paths.

## Related Patterns

- [Chain-Bound Request Hash](./pattern-chain-bound-request-hash.md)
- [Governance as Arbitrary Execution](../../ANTIPATTERNS.md#governance-as-arbitrary-execution)
- [Selector-Scoped Authority](../access-control/pattern-selector-scoped-authority.md)
