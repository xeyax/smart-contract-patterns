# Multi-Adapter Message Quorum

> Send cross-chain messages through multiple bridge adapters and execute only after a session-scoped quorum confirms the same payload.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, adapter, quorum, message, recovery |
| Complexity | High |
| Gas Efficiency | Low |
| Audit Risk | High |

## Use When

- A protocol cannot rely on one bridge transport for high-value state changes
- Multiple bridge adapters can independently authenticate the same session and payload
- Liveness recovery is needed when one adapter stalls or is disputed
- Message execution can tolerate extra latency and gas

## Avoid When

- All adapters share the same validator set or trust root
- The payload can be safely protected by one canonical bridge
- Adapter confirmation semantics cannot be normalized

## Trade-offs

**Pros:**
- Reduces dependence on one bridge transport
- Gives operators a recovery path when an adapter fails
- Makes transport-set changes explicit through session invalidation

**Cons:**
- Does not replace per-adapter replay protection
- Adds message bookkeeping and dispute complexity
- Quorum configuration can itself become a governance risk

## How It Works

A primary adapter carries the full message and secondary adapters carry the message hash. Execution waits until enough active adapters confirm the same session and hash:

```solidity
function receiveMessage(uint64 session, bytes32 messageHash, address adapter) external {
    require(activeAdapter[session][adapter], "inactive adapter");
    require(!confirmed[session][messageHash][adapter], "duplicate");

    confirmed[session][messageHash][adapter] = true;
    confirmationCount[session][messageHash]++;

    if (confirmationCount[session][messageHash] >= quorum[session]) {
        _markExecutable(session, messageHash);
    }
}
```

## Key Points

- Bind confirmations to an adapter-set session so membership changes do not mix old and new quorums.
- Count each adapter once per message hash.
- Keep dispute or recovery paths for stuck, malicious, or deprecated adapters.
- Reject recursive batch messages if nested execution can bypass quorum accounting.
- Treat quorum as transport agreement, not proof that the payload is economically safe.

## Source Evidence

- Centrifuge liquidity pools gateway sends a full message through a primary adapter and hash confirmations through secondary adapters.
- Its tests cover duplicate confirmations, quorum execution, adapter-set invalidation, recovery and challenge flows, and recursion guards.

## Related Patterns

- [Chain-Bound Request Hash](./pattern-chain-bound-request-hash.md)
- [Canonical Bridge Counterpart Validation](./pattern-canonical-bridge-counterpart-validation.md)
- [Bridge Message Replay](../../ANTIPATTERNS.md#bridge-message-replay)
