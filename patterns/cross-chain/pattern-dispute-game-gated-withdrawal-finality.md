# Dispute-Game Gated Withdrawal Finality

> Finalize rollup withdrawals only after the referenced output root is proven, mature, and accepted by the active dispute-game system.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, rollup, withdrawal, dispute-game, finality |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A rollup bridge releases assets from L2 withdrawal proofs on L1
- Output roots can be challenged by a fault or validity dispute process
- Proof maturity and finalization windows are part of the security model
- Governance can retire or blacklist invalid game types

## Avoid When

- The bridge has immediate canonical finality and no challenge mechanism
- The dispute game registry is not authenticated or can be swapped without delay
- Users need instant exits without accepting liquidity-provider or fast-bridge risk

## How It Works

Separate proof submission from finalization. The proof binds a withdrawal to an output root and message-passer storage proof. Finalization checks proof maturity plus the dispute game's validity:

```solidity
function proveWithdrawal(Withdrawal memory w, OutputProof memory proof) external {
    bytes32 root = _verifyOutputRootProof(proof);
    require(_verifyMessagePasserStorage(w, proof), "bad storage proof");
    provenWithdrawals[hashWithdrawal(w)] = Proven(root, block.timestamp, msg.sender);
}

function finalizeWithdrawal(Withdrawal memory w) external {
    Proven memory proof = provenWithdrawals[hashWithdrawal(w)];
    require(block.timestamp >= proof.timestamp + finalizationDelay, "immature");
    require(disputeRegistry.isOutputAccepted(proof.outputRoot), "disputed");
    require(!finalized[hashWithdrawal(w)], "finalized");

    finalized[hashWithdrawal(w)] = true;
    _releaseOrCall(w);
}
```

## Key Points

- Bind the withdrawal to output root, source storage proof, nonce, target, value, and caller domain.
- Require both proof maturity and dispute-game acceptance before custody changes.
- Reject outputs from retired, blacklisted, paused, or non-final games.
- Track finalization by normalized withdrawal hash.
- Treat proof and finalization pauses as exit-liveness risks that need expiry, monitoring, and emergency rules.

## Source Evidence

- Optimism Bedrock's portal proves withdrawals against output roots and message-passer storage, then finalizes only after proof maturity and dispute-game validity checks through the anchor-state registry.

## Related Patterns

- [Proof Bridge Exit Safety Requirements](./req-proof-bridge-exit-safety.md)
- [Bridge Exit Liveness Requirements](./req-bridge-exit-liveness.md)
- [Checkpointed Receipt Exit Proof](./pattern-checkpointed-receipt-exit-proof.md)
