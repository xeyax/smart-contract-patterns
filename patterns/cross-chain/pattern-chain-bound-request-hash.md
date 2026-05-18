# Chain-Bound Request Hash

> Bind cross-chain requests to source chain, destination chain, nonce, operation, participants, value, and payload before accepting remote confirmation.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, replay-protection, request-hash, finality, chain-binding |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | High |

## Use When

- A bridge mints, burns, unlocks, or confirms value on another chain
- The same bridge contracts or validators operate across multiple chains
- Requests can be retried, relayed, or confirmed asynchronously
- The protocol needs an on-chain replay ledger

## Avoid When

- The operation is local to one chain
- A canonical bridge already provides a complete non-replayable message id
- The bridge cannot authenticate the remote sender or source domain

## Trade-offs

**Pros:**
- Prevents valid requests from one chain being reused on another chain
- Gives every request a deterministic id for confirmation and deduplication
- Makes audits easier because the replay domain is explicit

**Cons:**
- Does not prove source-chain finality by itself
- Requires stable encoding across all bridge implementations
- Request hash changes can break pending messages during upgrades

## How It Works

Every bridge request is encoded with its full replay domain:

```solidity
requestHash = keccak256(abi.encode(
    operation,
    nonce,
    sourceChainId,
    destinationChainId,
    sender,
    receiver,
    token,
    amount,
    fee,
    extraData
));
```

The destination chain accepts confirmation only once:

```solidity
function confirm(Request calldata request, bytes calldata proof) external {
    bytes32 requestHash = hashRequest(request);

    require(request.destinationChainId == block.chainid, "wrong destination");
    require(!confirmed[requestHash], "already confirmed");
    _verifyRemoteRequest(requestHash, proof);

    confirmed[requestHash] = true;
    _complete(request);
}
```

## Key Points

- Include both source and destination chain ids.
- Include the operation type; a burn request must not replay as a mint request.
- Include all value-bearing fields, including fee, token, sender, receiver, and payload.
- Store confirmations by request hash, not by nonce alone.
- Validate the destination chain before irreversible actions such as burning.
- Pair request-hash replay protection with source-chain finality rules.
- Historical custodial wrappers may store local request hashes for auditability, but modern cross-chain bridges should bind the full operation and chain domain.

## Common Pitfalls

| Pitfall | Impact | Solution |
|---------|--------|----------|
| Nonce-only replay protection | Same nonce space can collide across chains or operations | Hash the full replay domain |
| Destination checked after burn | User can burn into an unsupported path | Check destination allowlist before burn |
| Confirmation without finality | Mint/unlock can happen for a reorged source event | Require finality depth or canonical bridge proof |
| Mutable hash schema | Pending messages become unconfirmable after upgrade | Version request encodings explicitly |

## Source Evidence

- FBTC hashes bridge requests with operation, nonce, source chain, destination chain, participants, amount, fee, and extra data.
- FBTC records cross-chain confirmations by request hash and tests duplicate confirmation rejection.
- WBTC stores request hashes for mint/burn request auditability, but its trusted-custodian model is not a substitute for chain-bound replay protection.

## Related Patterns

- [Historical Bounds](../oracles/pattern-historical-bounds.md) - guardrails for cross-chain price relays
- [Bridge Message Replay](../../ANTIPATTERNS.md#bridge-message-replay) - anti-pattern this mitigates
