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
- During collateral or output-asset migrations, include the intended output asset or token semantics so a valid old message cannot claim the wrong asset after cutover.
- Store confirmations by request hash, not by nonce alone.
- Consume approvals or validation records before minting, unlocking, or calling external recipients.
- Validate the destination chain before irreversible actions such as burning.
- Pair request-hash replay protection with source-chain finality rules.
- Historical custodial wrappers may store local request hashes for auditability, but modern cross-chain bridges should bind the full operation and chain domain.
- Proof-based exits may use a source transaction or log-location nullifier instead of an application request hash only when the checkpoint manager fixes the source domain, the destination contract fixes the peer/emitter, and equivalent proof encodings are normalized before hashing.
- Cross-chain mint or withdrawal monitors can add a single-use validation ledger around request hashes: requests move from unreported to reported to consumed, and even threshold-bypassed small transfers are marked consumed so they cannot be replayed later.
- Endpoint-native ledgers should still expose their replay domain clearly: receiver, source endpoint, remote sender, nonce, payload hash, destination chain, and route-specific auto-call fields are all part of the boundary.
- If a periphery signs or verifies opaque bridge calldata, revalidate the decoded destination route against the signed bytes before handing funds to the bridge.
- If replay protection is delegated to a canonical token bridge or message bus, document that trust boundary instead of implying the relayer contract owns the consumed-message ledger.

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
| Periphery parser drift | Signed bridge calldata proves one route while execution submits another | Bind and re-decode the exact calldata bytes, or pass one typed structure through validation and execution |

## Source Evidence

- FBTC hashes bridge requests with operation, nonce, source chain, destination chain, participants, amount, fee, and extra data.
- FBTC records cross-chain confirmations by request hash and tests duplicate confirmation rejection.
- WBTC stores request hashes for mint/burn request auditability, but its trusted-custodian model is not a substitute for chain-bound replay protection.
- Polygon PoS exits derive spent-exit nullifiers from proven source log location and normalized proof data while relying on checkpoint and child-emitter validation for the chain and peer domain.
- Noble's CCTP metadata wrapper pairs an EVM-side metadata message with a canonical CCTP burn nonce, showing why sidecar route data should reference the value-transfer identity rather than replace it.
- Lombard's bascule flow reports mint request ids, validates each id once, consumes bypassed small-transfer ids, and separates risk-increasing threshold changes from risk-reducing decreases.
- Axelar binds command id, source chain, source address, destination contract, payload hash, token symbol, and amount in gateway approval keys in [`contracts/AxelarGateway.sol`](https://github.com/axelarnetwork/axelar-cgp-solidity/blob/1736bfaa0e5e30207b142a5a53a27edf0f0a5c45/contracts/AxelarGateway.sol), then consumes approvals in `validateContractCall` and `validateContractCallAndMint` before execution.
- Gnosis xDAI bridge migration notes and message libraries show why bridge messages must bind intended token/output semantics during DAI-to-USDS collateral migration in [`USDSMigration.md`](https://github.com/gnosischain/tokenbridge-contracts/blob/52afd25b05f1afa3347f2f18595748b2149df6aa/USDSMigration.md) and `contracts/libraries/Message.sol`.
- Lorenzo `MintSecurity` domain-separates guardian mint hashes by chain id and contract address, binds BTC tx hash, token, destination, staking output index, inclusion height, and amount, then consumes hashes and sorts recovered signers to prevent duplicate-signature quorum in [`src/core/MintSecurity.sol`](https://github.com/Lorenzo-Protocol/enzoBTC_contract/blob/5951bff2cd51a3ac91a239ed6ca73aca095986dd/src/core/MintSecurity.sol).
- Fraxferry v1 commits cross-chain batch ranges and payload hashes before delayed execution in [`src/hardhat/contracts/Fraxferry/Fraxferry.sol`](https://github.com/FraxFinance/frax-solidity/blob/30532c8cefcbf5c7efafcff4369261bd435a4859/src/hardhat/contracts/Fraxferry/Fraxferry.sol); the batch hash gives replay and data-integrity structure but not trustless finality.
- Across V3 binds relay identity to origin chain, destination chain, deposit id, participants, tokens, amounts, deadlines, exclusivity, and message, then hashes with the local chain id in [`contracts/spoke-pools/SpokePool.sol`](https://github.com/across-protocol/contracts/blob/b4c4a46742dde83cbbace16ee066c6681b47ddee/contracts/spoke-pools/SpokePool.sol).
- LayerZero V2 records inbound payload hashes by receiver, source endpoint, remote sender, nonce, and payload hash, then clears the verified payload before receiver execution in [`packages/layerzero-v2/evm/protocol/contracts/MessagingChannel.sol`](https://github.com/LayerZero-Labs/LayerZero-v2/blob/9c741e7f9790639537b1710a203bcdfd73b0b9ac/packages/layerzero-v2/evm/protocol/contracts/MessagingChannel.sol) and `EndpointV2.sol`.
- deBridge computes submission ids from the debridge asset id, source chain, destination chain, amount, receiver, nonce, auto-call fee, fallback address, data hash, and native sender in [`contracts/transfers/DeBridgeGate.sol`](https://github.com/debridge-finance/debridge-contracts-v1/blob/2e9f9c73438738310b5293cec4cffe25741e9b1f/contracts/transfers/DeBridgeGate.sol).
- Socket packs source chain, sibling plug, destination chain, local plug, message id, execution params, and payload before switchboard proof verification in [`contracts/socket/SocketDst.sol`](https://github.com/SocketDotTech/socket-DL/blob/b2601e280533960df4d36eeef25ab81957f59eb9/contracts/socket/SocketDst.sol).
- Nomad formats messages with origin, sender, nonce, destination, recipient, and body in [`packages/contracts-core/contracts/libs/Message.sol`](https://github.com/nomad-xyz/monorepo/blob/b64c5aebbdc3d9fc8416ab1d18f93ea5b00f0411/packages/contracts-core/contracts/libs/Message.sol), while routers validate enrolled remote routers before dispatch.
- LI.FI Across V4 periphery validates signed bridge calldata against route fields before deposit in [`src/Facets/AcrossV4SwapFacet.sol`](https://github.com/lifinance/contracts/blob/7aeb2419d52d6bf834bf2c47e54dd8ea470a57bd/src/Facets/AcrossV4SwapFacet.sol) and `src/Facets/CalldataVerificationFacet.sol`.

## Related Patterns

- [Historical Bounds](../oracles/pattern-historical-bounds.md) - guardrails for cross-chain price relays
- [Checkpointed Receipt Exit Proof](./pattern-checkpointed-receipt-exit-proof.md)
- [Route-Scoped DVN Quorum](./pattern-route-scoped-dvn-quorum.md)
- [Break-Glass Risk Limiter](../access-control/pattern-break-glass-risk-limiter.md)
- [Dispute-Windowed Operator Batch Bridge](./pattern-dispute-windowed-operator-batch-bridge.md)
- [Bridge Message Replay](../../ANTIPATTERNS.md#bridge-message-replay) - anti-pattern this mitigates
