# Epoch-Committed Validator Set Header

> Commit each epoch's validator-set root, quorum rule, key tag, and capture timestamp before verifying epoch-scoped messages.

## Metadata

| Property | Value |
|----------|-------|
| Category | governance |
| Tags | governance, validator-set, epoch, quorum, relay |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A relay or settlement layer verifies messages against changing validator sets
- Validator membership and voting power are sampled at discrete epochs
- Verification logic may differ by key type, chain, or network
- Later proofs need a stable commitment to the sampled set

## Avoid When

- Validator membership changes must take effect immediately
- The system cannot define an objective epoch boundary
- Quorum and key semantics are off-chain social process
- A light client already verifies the full validator set directly

## How It Works

Each epoch stores a header that commits the validator-set root and verification parameters:

```solidity
struct EpochHeader {
    bytes32 validatorSetRoot;
    uint48 captureTimestamp;
    uint32 quorumBps;
    bytes32 keyTag;
    address verifier;
}

function commitEpoch(uint256 epoch, EpochHeader calldata header) external {
    require(epoch == lastCommittedEpoch + 1, "non-sequential");
    require(header.captureTimestamp <= block.timestamp, "future");
    headers[epoch] = header;
}
```

Message verification loads the header for the target epoch and delegates signature or proof checks to the committed verifier parameters.

## Key Points

- Enforce sequential epoch commits or explicitly document skipped epochs.
- Bind verifier extras, key type, quorum threshold, and capture timestamp into the header.
- Keep validator-key registry snapshots compatible with the capture timestamp.
- Define what happens if an epoch cannot be committed.
- Test stale headers, wrong key tags, quorum drift, and verifier replacement.

## Source Evidence

- Symbiotic Relay commits sequential settlement headers containing validator-set roots, quorum parameters, key tags, capture timestamps, and verifier extras, then tests epoch-scoped verification paths.

## Related Patterns

- [Self-Authenticated Key Registry](../access-control/pattern-self-authenticated-key-registry.md)
- [Composable Voting-Power Calculator](./pattern-composable-voting-power-calculator.md)
