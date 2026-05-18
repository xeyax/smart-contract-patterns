# Bitcoin SPV State Transition Gate

> Gate bridge state transitions on Bitcoin transaction, merkle, coinbase, and difficulty proofs while documenting maintainer trust boundaries.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, bitcoin, spv, proof, finality |
| Complexity | High |
| Gas Efficiency | Low |
| Audit Risk | High |

## Use When

- An EVM bridge must verify Bitcoin deposits, sweeps, redemptions, or fraud evidence
- A relay or light-client contract tracks headers and difficulty epochs
- State transitions depend on transaction inclusion in Bitcoin blocks
- The protocol can document any trusted proof-submitter or relay-maintainer assumptions

## Avoid When

- The protocol cannot validate enough Bitcoin headers or difficulty information
- A centralized operator is the real source of truth and no SPV checks are meaningful
- Users expect trustless Bitcoin finality but the relay depends on trusted maintainers

## How It Works

Verify transaction inclusion and header validity before changing bridge state:

```solidity
function submitDepositSweepProof(SweepProof calldata proof) external {
    require(lightRelay.isKnownHeader(proof.header), "unknown header");
    require(_validDifficultyEpoch(proof.header), "bad difficulty");
    require(_verifyMerkleProof(proof.txid, proof.txMerkleProof, proof.header), "bad tx proof");
    require(_verifyCoinbaseIfNeeded(proof.coinbase), "bad coinbase");

    _finalizeSweep(proof.txid);
}
```

If the system relies on trusted maintainers to submit canonical headers, that trust boundary is part of the pattern, not an implementation detail.

## Key Points

- Verify transaction inclusion, block header linkage, target difficulty, and required confirmations.
- Bind the proven Bitcoin transaction to the expected bridge wallet, outpoint, value, and script.
- Reject proof reuse with normalized nullifiers.
- Keep relay maintainer authority, challenge windows, and emergency replacement procedures explicit.
- Do not claim proof of work alone proves canonical Bitcoin mainnet inclusion when the relay input is trusted.

## Source Evidence

- tBTC v2 gates deposit sweeps and bridge transitions on Bitcoin transaction and relay proofs, with comments documenting that proof submission can prove work but still rely on maintainer trust for canonical mainnet inclusion.

## Related Patterns

- [Proof Bridge Exit Safety Requirements](./req-proof-bridge-exit-safety.md)
- [Checkpointed Receipt Exit Proof](./pattern-checkpointed-receipt-exit-proof.md)
- [Self-Describing UTXO Deposit Reveal](./pattern-self-describing-utxo-deposit-reveal.md)
