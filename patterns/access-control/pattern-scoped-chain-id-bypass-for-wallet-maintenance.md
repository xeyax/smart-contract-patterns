# Scoped Chain-ID Bypass For Wallet Maintenance

> Allow replayable smart-wallet maintenance only through self-calls, selector allowlists, and reserved nonce domains, never through arbitrary value execution.

## Metadata

| Property | Value |
|----------|-------|
| Category | access-control |
| Tags | access-control, wallet, chain-id, replay, account-abstraction |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A smart account needs the same owner-maintenance operation on multiple chains
- The operation is wallet-internal and does not move protocol custody or settle value
- EntryPoint, nonce key, target, selector, and calldata shape can be tightly constrained
- Users understand that the maintenance operation is intentionally replayable

## Avoid When

- The action mints, burns, bridges, withdraws, swaps, or changes protocol value
- Calls can target arbitrary contracts or arbitrary wallet functions
- Nonce domains are shared with ordinary user operations
- Chain-specific owner state must not be synchronized

## Trade-offs

**Pros:**
- One signature maintains owner state on every chain, avoiding a per-chain signing ceremony
- The bypass lane is tightly fenced: self-call only, fixed selector allowlist, zero value, EntryPoint-mediated
- A reserved nonce key keeps replayable operations from colliding with ordinary user operations
- Value-bearing and protocol-facing operations remain fully chain-bound

**Cons:**
- Every allowlisted selector is a cross-chain replay vector; one mis-scoped selector compromises the wallet on all chains at once
- Replay is unordered across chains, so owner state can desync when maintenance operations land in different orders or skip chains
- The bypass predicate spans caller, nonce key, target, selector, and value; a subtle calldata-parsing bug in any check is catastrophic
- A signed maintenance operation can execute on chains the user never intended to use, which is hard to convey in signing UX
- Expanding the selector allowlist later is a high-risk security change for already-deployed wallets

## How It Works

Permit chain-id omission only for a small maintenance lane:

```solidity
function canSkipChainIdValidation(UserOperation calldata op) public view returns (bool) {
    return msg.sender == address(entryPoint)
        && op.nonce >> 64 == REPLAYABLE_MAINTENANCE_KEY
        && op.callData.target == address(this)
        && allowedMaintenanceSelector[op.callData.selector]
        && op.callData.value == 0;
}
```

All other operations keep normal chain-bound signatures.

## Key Points

- Restrict caller to the account abstraction entry point or equivalent wallet execution gateway.
- Restrict target to `address(this)` and selectors to a fixed maintenance allowlist.
- Use a reserved nonce key so replayable operations cannot collide with ordinary user operations.
- Disallow value movement and arbitrary execution in the bypass lane.
- Treat selector changes as high-risk wallet security changes.
- Keep bridge, mint, burn, settlement, and custody requests chain-bound.

## Source Evidence

- Coinbase Smart Wallet supports a narrowly scoped chain-id bypass for owner maintenance through EntryPoint-mediated self-calls, selector checks, and reserved nonce-key behavior.

## Related Patterns

- [Chain-Bound Request Hash](../cross-chain/pattern-chain-bound-request-hash.md)
- [ERC-1271 Replay-Safe Account Signatures](./pattern-erc1271-replay-safe-account-signatures.md)
- [Signature Scope Drift](../../ANTIPATTERNS.md#signature-scope-drift)
