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

## Trade-offs

**Pros:**
- Proofs verify against a stable committed snapshot, so validator churn cannot retroactively invalidate or forge epoch-scoped messages.
- Binding quorum, key tag, and verifier into the header prevents mixing verification parameters across epochs.
- Storage stays bounded when only the proof-window of validator sets is retained.
- Verifier indirection lets key types and proof schemes evolve per epoch without redeploying the settlement layer.

**Cons:**
- Validator membership changes only take effect at epoch boundaries, delaying removal of compromised keys.
- A missed or contested epoch commit halts verification for that epoch; the failure path must be designed and governed.
- The committer role is a trust chokepoint: a bad header commits wrong quorum or root for the whole epoch.
- High audit surface: stale headers, wrong key tags, quorum drift, and verifier replacement all need dedicated tests.
- Sequential-commit enforcement adds liveness coupling — one stuck epoch blocks all later commits.

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
- For weighted operator sets, require sorted unique signers and bind the validator-set epoch into the proof.
- Retain recent validator sets only for the proof window, and require current-epoch authority for operator-set rotation.
- Define what happens if an epoch cannot be committed.
- Test stale headers, wrong key tags, quorum drift, and verifier replacement.

## Source Evidence

- Symbiotic Relay commits sequential settlement headers containing validator-set roots, quorum parameters, key tags, capture timestamps, and verifier extras, then tests epoch-scoped verification paths.
- Axelar weighted auth validates operator proofs and rotates operatorship in [`contracts/auth/AxelarAuthWeighted.sol`](https://github.com/axelarnetwork/axelar-cgp-solidity/blob/1736bfaa0e5e30207b142a5a53a27edf0f0a5c45/contracts/auth/AxelarAuthWeighted.sol) through `validateProof`, `_validateSignatures`, and `_transferOperatorship`, with tests in `test/auth/AxelarAuthWeighted.js`.

## Related Patterns

- [Self-Authenticated Key Registry](../access-control/pattern-self-authenticated-key-registry.md)
- [Composable Voting-Power Calculator](./pattern-composable-voting-power-calculator.md)
