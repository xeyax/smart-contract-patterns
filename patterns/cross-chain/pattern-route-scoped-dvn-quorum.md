# Route-Scoped DVN Quorum

> Configure required and optional verifier sets per remote route, then accept a packet only when required verifiers and an optional threshold satisfy the route policy.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, dvn, quorum, verifier, confirmation |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A messaging route can choose its own verifier set and confirmation policy
- Some verifiers must always attest, while others form an optional threshold
- The endpoint can record verification before application execution
- Default verifier policy can be overridden by higher-risk applications or routes

## Avoid When

- Verifier identities, thresholds, or confirmation counts can change without delay or monitoring
- Adapter transports cannot preserve the configured confirmation semantics
- The packet hash omits the source endpoint, destination endpoint, sender, receiver, nonce, or payload hash
- Verification immediately performs non-idempotent application logic

## Trade-offs

**Pros:**
- Lets high-value routes use stronger verification than low-value routes
- Separates verifier policy from generic endpoint replay handling
- Supports required witnesses plus flexible optional quorum

**Cons:**
- Configuration mistakes can silently weaken one route
- Optional thresholds are harder to reason about than one fixed multisig
- External adapter verifiers may have different finality semantics

## How It Works

Each route resolves a verifier policy. Required verifiers must all attest with
enough source confirmations, and optional verifiers must meet a threshold:

```solidity
struct VerifierPolicy {
    uint64 confirmations;
    address[] required;
    address[] optional;
    uint8 optionalThreshold;
}

function commitVerification(Route calldata route, bytes32 payloadHash) external {
    VerifierPolicy memory policy = _resolvePolicy(route.receiver, route.srcDomain);
    require(_allRequiredVerified(policy, route.headerHash, payloadHash), "required");
    require(_optionalThresholdVerified(policy, route.headerHash, payloadHash), "optional");
    endpoint.verify(route.origin, route.receiver, payloadHash);
}
```

## Implementation

```solidity
function _checkPolicy(VerifierPolicy memory policy) internal pure {
    require(policy.required.length > 0 || policy.optionalThreshold > 0, "no verifiers");
    require(policy.optionalThreshold <= policy.optional.length, "bad threshold");
    _requireSortedUnique(policy.required);
    _requireSortedUnique(policy.optional);
}
```

### Key Points

- Validate at least one verifier path after resolving defaults and overrides.
- Require sorted, duplicate-free verifier lists so one key cannot count twice.
- Bind verifier attestations to the canonical packet header and payload hash.
- Treat confirmation count changes as risk-increasing when they lower finality.
- Document adapter-specific confirmation drift when a verifier bridge forwards a packet without respecting route confirmations.
- Test duplicate verifiers, zero-verifier policies, threshold bounds, wrong destination endpoint, and insufficient confirmations.

## Source Evidence

- LayerZero V2 ULN configuration stores confirmations, required DVNs, optional DVNs, and optional threshold in [`packages/layerzero-v2/evm/messagelib/contracts/uln/UlnBase.sol:8`](https://github.com/LayerZero-Labs/LayerZero-v2/blob/9c741e7f9790639537b1710a203bcdfd73b0b9ac/packages/layerzero-v2/evm/messagelib/contracts/uln/UlnBase.sol#L8).
- LayerZero V2 resolves defaults and still requires at least one verifier path in `UlnBase.sol:74`.
- LayerZero V2 validates counts, thresholds, maximum sizes, and duplicate-free verifier lists in `UlnBase.sol:150`.
- LayerZero V2 receive verification checks that required DVNs have signed and that optional DVNs meet threshold in [`packages/layerzero-v2/evm/messagelib/contracts/uln/ReceiveUlnBase.sol:90`](https://github.com/LayerZero-Labs/LayerZero-v2/blob/9c741e7f9790639537b1710a203bcdfd73b0b9ac/packages/layerzero-v2/evm/messagelib/contracts/uln/ReceiveUlnBase.sol#L90).
- LayerZero V2 tests cover invalid ULN configurations in [`packages/layerzero-v2/evm/messagelib/test/UlnBase.t.sol`](https://github.com/LayerZero-Labs/LayerZero-v2/blob/9c741e7f9790639537b1710a203bcdfd73b0b9ac/packages/layerzero-v2/evm/messagelib/test/UlnBase.t.sol).

## Real-World Examples

- LayerZero V2 - ULN verifier policy is resolved per OApp and remote endpoint with required and optional DVN sets.

## Related Patterns

- [Recipient-Scoped Message Verifier](./pattern-recipient-scoped-message-verifier.md)
- [Stake-Backed DVN Verifier Adapter](./pattern-stake-backed-dvn-verifier-adapter.md)
- [Multi-Adapter Message Quorum](./pattern-multi-adapter-message-quorum.md)
- [Divergent Message Parsing Between Authorization And Execution](../../ANTIPATTERNS.md#divergent-message-parsing-between-authorization-and-execution)

## References

- See Source Evidence.
