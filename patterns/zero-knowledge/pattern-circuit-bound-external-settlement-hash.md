# Circuit-Bound External Settlement Hash

> Hash settlement fields outside the circuit, constrain the hash as a public input, and verify the same hash on-chain before moving tokens.

## Metadata

| Property | Value |
|----------|-------|
| Category | zero-knowledge |
| Tags | zk, settlement, ext-data, hash, replay-protection |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A zk proof controls public token deposits or withdrawals
- Recipient, relayer, fee, or refund fields are too large to pass individually through the circuit
- Settlement data must remain visible on-chain
- The circuit and contract can share an exact encoding

## Avoid When

- The external data encoding is ambiguous or versionless
- Different contracts reuse the same hash domain
- Settlement fields are not value-bearing
- The circuit can directly constrain every field with acceptable cost

## How It Works

The prover supplies external settlement data and the circuit constrains its hash. The contract recomputes that hash before accepting the proof:

```solidity
function transact(Proof calldata proof, ExtData calldata extData) external {
    bytes32 extDataHash = hashExtData(extData);
    require(extDataHash == proof.publicInputs.extDataHash, "ext data");
    _verifyProof(proof);
    _settle(extData);
}
```

Changing the recipient, fee, relayer, or refund address changes the hash and invalidates the proof.

## Key Points

- Use a single canonical encoder in tests and production tooling.
- Domain-separate by chain, pool, circuit version, and settlement action.
- Reject malformed or out-of-range external fields before token movement.
- Test proof failure when each settlement field is modified.
- Keep balance-delta checks around external token transfers.

## Source Evidence

- Tornado Nova hashes external settlement data into constrained public inputs and verifies the same hash on-chain before executing pool token settlement.

## Related Patterns

- [Shielded Pool Accounting Invariants](./req-shielded-pool-accounting-invariants.md)
- [Chain-Bound Request Hash](../cross-chain/pattern-chain-bound-request-hash.md)
