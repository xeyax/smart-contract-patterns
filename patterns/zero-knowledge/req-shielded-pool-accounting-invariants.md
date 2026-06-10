# Shielded Pool Accounting Invariants

> Requirements for private-transfer pools where zk proofs update an on-chain balance tree and external token settlement happens outside the circuit.

## Metadata

| Property | Value |
|----------|-------|
| Category | zero-knowledge |
| Tags | zk, shielded-pool, nullifier, accounting, invariant |
| Type | Requirement |

## R1: Known Root Membership

**Every proof must reference a recent root that the pool has accepted.**

### What This Means

- Old roots are retained only for a bounded history window.
- Unknown roots are rejected before state changes.
- Root history size is chosen for expected proof-generation delay.

## R2: Nullifiers Are Unique

**Input nullifiers cannot be reused within the transaction or across prior transactions.**

### What This Means

- On-chain spent-nullifier storage is checked before accepting the proof.
- The circuit rejects duplicate input nullifiers in the same proof.
- Failed external settlement cannot leave nullifiers consumed without an explicit recovery design.

## R3: Public Amounts Conserve Value

**Public deposit and withdrawal amounts must match the constrained circuit public inputs and on-chain token movement.**

### What This Means

- External amount hashes are bound into the proof.
- Output amounts are range-constrained.
- On-chain settlement verifies token balance deltas or explicit transfer amounts.

## R4: External Settlement Is Bound

**Recipient, relayer, fee, refund, and ext-data fields that control settlement are committed by the proof.**

### What This Means

- The proof cannot be replayed with a different receiver or relayer fee.
- Hashing format and domain separation are stable across circuit and contract code.
- Tests cover modified ext-data rejection.

## Source Evidence

- Tornado Nova checks known roots, spent nullifiers, duplicate in-proof nullifiers, public amount conservation, range constraints, and external settlement data hashes across contract, circuit, and tests.

## Related Patterns

- [Bounded Merkle Root History](./pattern-bounded-merkle-root-history.md)
- [Circuit-Bound External Settlement Hash](./pattern-circuit-bound-external-settlement-hash.md)
