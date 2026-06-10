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

## Trade-offs

**Pros:**
- On-chain SPV verification removes reliance on a single attestor for Bitcoin inclusion claims.
- Normalized nullifiers stop the same Bitcoin transaction from being credited twice.
- Difficulty-epoch and coinbase checks raise the cost of fabricated-header attacks well above a bare merkle proof.
- Explicit maintainer trust boundaries keep audits and user expectations aligned with what is actually verified.

**Cons:**
- Header, merkle, and difficulty verification is gas-heavy, and relayers carry significant off-chain proof-construction burden.
- Trusted relay maintainers remain a liveness and censorship chokepoint; proof of work alone cannot establish canonical mainnet inclusion.
- Deep Bitcoin reorgs force coordinated repair of staking state, voting power, and reward indexes — complex, rarely exercised recovery code.
- Script parsing, endianness handling, merkle verification, and difficulty retargeting are classic bug sources, inflating audit surface.
- Required confirmation depth adds hours of latency to deposits and state transitions.

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
- For BTC staking, distinguish activation finality from exit intent: voting power should require canonical/deep enough staking inclusion, while an unbonding spend proof may revoke stake before deep finality.
- Large reorg repair must update staking state, voting power, and reward indexes together.

## Source Evidence

- tBTC v2 gates deposit sweeps and bridge transitions on Bitcoin transaction and relay proofs, with comments documenting that proof submission can prove work but still rely on maintainer trust for canonical mainnet inclusion.
- Babylon BTC staking documentation distinguishes activation finality from unbonding intent and describes reorg repair across staking, voting-power, and reward indexes.
- Lorenzo validates Bitcoin header linkage and cumulative work, stores canonical light-client state, verifies merkle inclusion before staking mint flows, and applies source-finality checks in [`x/btclightclient`](https://github.com/Lorenzo-Protocol/lorenzo/blob/ee65c41e485ad7b57f4e40d0230c029354610a7d/x/btclightclient) and `x/btcstaking`.

## Related Patterns

- [Proof Bridge Exit Safety Requirements](./req-proof-bridge-exit-safety.md)
- [Checkpointed Receipt Exit Proof](./pattern-checkpointed-receipt-exit-proof.md)
- [Self-Describing UTXO Deposit Reveal](./pattern-self-describing-utxo-deposit-reveal.md)
- [Covenant-Gated Bitcoin Staking Output](./pattern-covenant-gated-bitcoin-staking-output.md)
- [Value-Tiered Source Finality](./pattern-value-tiered-source-finality.md)
