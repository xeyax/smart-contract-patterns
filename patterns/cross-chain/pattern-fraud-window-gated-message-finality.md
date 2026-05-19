# Fraud-Window Gated Message Finality

> Finalize optimistic rollup withdrawals only after the referenced state root is outside the fraud window and the message-passer storage proof verifies.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, rollup, withdrawal, fraud-window, finality |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A legacy optimistic rollup bridge releases L1 assets from L2 withdrawal proofs
- State roots can be deleted or challenged during a fixed fraud-proof window
- Withdrawal finality is based on elapsed fraud window plus inclusion proofs, not an active dispute-game registry
- Users can tolerate delayed exits in exchange for canonical bridge security

## Avoid When

- The rollup uses active dispute games, output proposals, or validity proofs with different finality semantics
- The state-root publisher or fraud verifier can change the fraud window without bounds or delay
- Fast exits are provided by liquidity providers and do not rely on canonical proof finality
- The bridge cannot verify the message-passer storage slot for the withdrawal payload

## How It Works

The bridge verifies two facts before releasing custody or executing the L1
message:

1. The state root batch that contains the withdrawal is no longer inside the
   fraud-proof window.
2. The L2 message-passer storage proof proves that the exact cross-domain
   message was recorded under that state root.

```solidity
function finalizeWithdrawal(Message calldata message, Proof calldata proof) external {
    require(!stateCommitmentChain.insideFraudProofWindow(proof.batch), "fraud window");
    require(stateCommitmentChain.verifyStateCommitment(
        proof.stateRoot,
        proof.batch,
        proof.stateRootProof
    ), "bad state root");
    require(_verifyMessagePasserStorage(message, proof.storageProof), "bad message proof");

    bytes32 id = _withdrawalHash(message);
    require(!finalized[id], "finalized");
    finalized[id] = true;
    _releaseOrCall(message);
}
```

Fraud verifiers can delete invalid state batches only while the batch is still
inside the fraud window. After that window closes, finalized withdrawals depend
on the stored state root and message-passer proof.

## Key Points

- Keep this separate from dispute-game gated finality; the acceptance predicate is elapsed fraud window, not game resolution.
- Bind finalization to the exact cross-domain calldata or withdrawal hash.
- Verify both state-root inclusion and message-passer storage inclusion.
- Bound and govern fraud-window changes because they directly affect exit safety and liveness.
- Track finalized withdrawals by normalized hash before external calls.
- Document what happens if a state batch is deleted, paused, or superseded during the fraud window.

## Source Evidence

- Mantle's legacy L1 messenger accepts an L2-to-L1 message only when `insideFraudProofWindow` is false and state-root plus storage proofs verify in `/private/tmp/defillama-source/mantlenetworkio__mantle/packages/contracts/contracts/L1/messaging/L1CrossDomainMessenger.sol`.
- Mantle's `StateCommitmentChain` permits fraud-verifier deletion only while a batch is inside the fraud-proof window in `/private/tmp/defillama-source/mantlenetworkio__mantle/packages/contracts/contracts/L1/rollup/StateCommitmentChain.sol`.

## Related Patterns

- [Proof Bridge Exit Safety Requirements](./req-proof-bridge-exit-safety.md)
- [Bridge Exit Liveness Requirements](./req-bridge-exit-liveness.md)
- [Dispute-Game Gated Withdrawal Finality](./pattern-dispute-game-gated-withdrawal-finality.md)
