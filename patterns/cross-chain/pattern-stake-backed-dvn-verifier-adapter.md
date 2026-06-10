# Stake-Backed DVN Verifier Adapter

> Plug an external stake-backed validator-set proof into a bridge verifier lane, then forward the verified packet to the canonical receive library.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, dvn, verifier, validator-set, quorum |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A bridge or messaging layer supports custom verifier lanes
- An external settlement contract commits epoch-scoped validator sets and quorum rules
- Packets have a canonical domain-bound envelope
- The receive library has idempotent verification or commit semantics

## Avoid When

- The packet hash omits source chain, destination chain, nonce, sender, receiver, or payload domain
- The external validator set is not slashable, observable, or epoch-scoped
- Verification success directly executes non-idempotent application logic
- The worker network cannot persist packet and proof state

## Trade-offs

**Pros:**
- Verification is backed by slashable, epoch-scoped external stake rather than a goodwill-only DVN.
- Epoch binding bounds the window in which a stale or rotated validator set can sign packets.
- The adapter plugs into existing receive-library lanes, requiring no application-side changes.
- Hash-committed signer sets keep on-chain storage small while still validating full signer and power arrays.

**Cons:**
- Per-packet quorum proof verification over signer arrays is gas-heavy.
- It is a single verifier lane, not multi-adapter quorum: compromising the staked set compromises every packet on the lane.
- Safety leans on downstream receive-library idempotence; non-idempotent commits turn verified races into double execution.
- The off-chain worker must durably persist packet and proof state across the sent → proof → verify → commit pipeline — ongoing operational burden.
- Emergency signer resets are trusted recovery backdoors that need separate governance, delay, and monitoring.

## How It Works

The adapter reconstructs the canonical packet hash, verifies an epoch-scoped quorum proof, then records verification in the bridge receive library:

```solidity
function verifyPacket(Packet calldata packet, Proof calldata proof, uint256 epoch) external {
    bytes32 packetHash = _canonicalPacketHash(packet);
    require(settlement.verify(epoch, packetHash, proof), "quorum");
    receiveLibrary.verify(packet.header, packet.payloadHash);
}
```

This is one verifier path backed by external economic security. It is not the same as multi-adapter message quorum, where several transports must independently agree.

## Key Points

- Hash the bridge's canonical packet envelope, not an ad hoc subset of fields.
- Bind proof verification to the validator-set epoch and committed key type.
- Treat already-verified races as safe only when the downstream receive library is idempotent.
- Monitor the full `sent -> proof -> verify -> commit/execution` path.
- Document whether this adapter is production-proven, simulation-grade, or experimental.
- If the external signer set is hash-committed, verify the supplied signer and power arrays against that commitment before checking quorum.
- Keep emergency signer resets separate from ordinary quorum verification and document them as trusted recovery paths.

## Source Evidence

- GAIB's Symbiotic Super Sum simulation integrates a Symbiotic-backed LayerZero DVN that verifies an epoch-bound quorum proof before calling the LayerZero receive verification library. The repository labels the setup as high-fidelity but not production-ready.
- Celer SGN bridge verifies signer and power arrays against a committed signer-set hash, requires more than two-thirds signed power, and provides a delayed owner emergency reset path in [`contracts/liquidity-bridge/Signers.sol`](https://github.com/celer-network/sgn-v2-contracts/blob/b8a27161e0b700e30f30452c73418b60d133163f/contracts/liquidity-bridge/Signers.sol).

## Related Patterns

- [Epoch-Committed Validator Set Header](../governance/pattern-epoch-committed-validator-set-header.md)
- [Canonical Bridge Counterpart Validation](./pattern-canonical-bridge-counterpart-validation.md)
- [Operation Cadence Liveness Agent](../monitoring/pattern-operation-cadence-liveness-agent.md)
