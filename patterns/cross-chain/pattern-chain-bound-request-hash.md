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
- Consume approvals or validation records before minting, unlocking, or calling external recipients.
- Validate the destination chain before irreversible actions such as burning.
- Pair request-hash replay protection with source-chain finality rules.
- Historical custodial wrappers may store local request hashes for auditability, but modern cross-chain bridges should bind the full operation and chain domain.
- Proof-based exits may use a source transaction or log-location nullifier instead of an application request hash only when the checkpoint manager fixes the source domain, the destination contract fixes the peer/emitter, and equivalent proof encodings are normalized before hashing.
- Cross-chain mint or withdrawal monitors can add a single-use validation ledger around request hashes: requests move from unreported to reported to consumed, and even threshold-bypassed small transfers are marked consumed so they cannot be replayed later.

### Sidecar Metadata Beside Canonical Value Messages

When a canonical bridge transfer cannot carry application routing data directly, a companion metadata message can be used only if it commits to the canonical value-transfer identity:

```solidity
metadataHash = keccak256(abi.encode(
    canonicalMessageNonce,
    sourceSender,
    destinationDomain,
    destinationRecipient,
    routeFields,
    schemaVersion
));
```

The sidecar must not mint, unlock, or release value independently. Destination logic should reject unpaired metadata and treat missing or malformed metadata as a liveness/recovery case, not as proof of value settlement.

## Common Pitfalls

| Pitfall | Impact | Solution |
|---------|--------|----------|
| Nonce-only replay protection | Same nonce space can collide across chains or operations | Hash the full replay domain |
| Destination checked after burn | User can burn into an unsupported path | Check destination allowlist before burn |
| Confirmation without finality | Mint/unlock can happen for a reorged source event | Require finality depth or canonical bridge proof |
| Mutable hash schema | Pending messages become unconfirmable after upgrade | Version request encodings explicitly |
| Unpaired metadata sidecar | Value settles without route data or route data applies to wrong transfer | Commit sidecar to canonical message id and schema |
| Bypassed request not consumed | Small transfer can be replayed after threshold changes | Mark every accepted request id consumed, including bypassed paths |

## Source Evidence

- FBTC hashes bridge requests with operation, nonce, source chain, destination chain, participants, amount, fee, and extra data.
- FBTC records cross-chain confirmations by request hash and tests duplicate confirmation rejection.
- WBTC stores request hashes for mint/burn request auditability, but its trusted-custodian model is not a substitute for chain-bound replay protection.
- Polygon PoS exits derive spent-exit nullifiers from proven source log location and normalized proof data while relying on checkpoint and child-emitter validation for the chain and peer domain.
- Noble's CCTP metadata wrapper pairs an EVM-side metadata message with a canonical CCTP burn nonce, showing why sidecar route data should reference the value-transfer identity rather than replace it.
- Lombard's bascule flow reports mint request ids, validates each id once, consumes bypassed small-transfer ids, and separates risk-increasing threshold changes from risk-reducing decreases.
- Axelar binds command id, source chain, source address, destination contract, payload hash, token symbol, and amount in gateway approval keys in `/private/tmp/defillama-source/axelarnetwork__axelar-cgp-solidity/contracts/AxelarGateway.sol`, then consumes approvals in `validateContractCall` and `validateContractCallAndMint` before execution.

## Related Patterns

- [Historical Bounds](../oracles/pattern-historical-bounds.md) - guardrails for cross-chain price relays
- [Checkpointed Receipt Exit Proof](./pattern-checkpointed-receipt-exit-proof.md)
- [Break-Glass Risk Limiter](../access-control/pattern-break-glass-risk-limiter.md)
- [Bridge Message Replay](../../ANTIPATTERNS.md#bridge-message-replay) - anti-pattern this mitigates
