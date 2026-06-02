# Self-Authenticated Key Registry

> Let operators register protocol keys only after proving control of the key, then snapshot key history for epoch-scoped verification.

## Metadata

| Property | Value |
|----------|-------|
| Category | access-control |
| Tags | access-control, key-registry, operator, signature, epoch |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Operators need off-chain signing, consensus, or relay keys distinct from owner accounts
- The protocol must prevent registering keys without key-holder consent
- Historical key state matters for validating prior epochs
- Key rotation should be public and auditable

## Avoid When

- Governance must explicitly approve every key before use
- Key ownership cannot be proven on-chain
- Historical snapshots are unnecessary and current-state lookup is sufficient
- The registry key can authorize fund movement without additional quorum checks

## How It Works

Require a signature or proof from the registered key over the operator, registry, and key type:

```solidity
function registerKey(bytes calldata key, bytes calldata proof) external {
    bytes32 digest = keccak256(abi.encode(
        "REGISTER_KEY",
        block.chainid,
        address(this),
        msg.sender,
        key
    ));
    require(_keySigned(key, digest, proof), "key proof");
    _checkpointKey(msg.sender, key);
}
```

Verification reads the key at the epoch or capture timestamp relevant to the message being verified, not necessarily the current key.

## Key Points

- Bind key proofs to chain, registry, operator, key type, and registration action.
- Store historical checkpoints for epoch validation.
- Define replacement and deletion semantics separately.
- Do not let key registration bypass stake, vault, or operator eligibility checks.
- Test proof reuse, wrong operator, wrong key type, and historical lookup boundaries.

## Source Evidence

- Symbiotic Relay operators self-register keys by proving key ownership, and tests cover key registration, rotation, historical snapshots, and epoch-specific reads.

## Related Patterns

- [Epoch-Committed Validator Set Header](../governance/pattern-epoch-committed-validator-set-header.md)
- [Signature Scope Drift](../../ANTIPATTERNS.md#signature-scope-drift)
