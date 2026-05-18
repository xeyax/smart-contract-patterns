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

## Source Evidence

- GAIB's Symbiotic Super Sum simulation integrates a Symbiotic-backed LayerZero DVN that verifies an epoch-bound quorum proof before calling the LayerZero receive verification library. The repository labels the setup as high-fidelity but not production-ready.

## Related Patterns

- [Epoch-Committed Validator Set Header](../governance/pattern-epoch-committed-validator-set-header.md)
- [Canonical Bridge Counterpart Validation](./pattern-canonical-bridge-counterpart-validation.md)
- [Operation Cadence Liveness Agent](../monitoring/pattern-operation-cadence-liveness-agent.md)
