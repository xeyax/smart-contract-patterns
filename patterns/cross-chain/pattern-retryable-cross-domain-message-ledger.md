# Retryable Cross-Domain Message Ledger

> Record successful and failed cross-domain message executions so failed deliveries can be retried while successful deliveries remain exact-once.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, messenger, retry, replay, exact-once |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Cross-domain messages execute arbitrary destination calls
- Destination execution can fail because of gas, receiver logic, or temporary dependencies
- The bridge can authenticate source domain, source sender, nonce, and payload
- Users need retry liveness without allowing successful messages to run twice

## Avoid When

- A failed destination call must automatically refund value instead of retrying
- Message identity omits source domain, destination domain, nonce, or payload
- The bridge cannot distinguish failed execution from unproven or unauthenticated messages

## Trade-offs

**Pros:**
- Failed deliveries stay retryable without sacrificing exact-once semantics for successful messages.
- Hashing the full versioned envelope blocks replay across chains, nonces, and gas-limit variants.
- The delivery-first variant decouples relayer payment from receiver-application failures.
- Gas-limit replay rescues underfunded queued messages without minting new message identities.

**Cons:**
- Per-message success/failed/delivered markers consume permanent storage for every cross-domain message.
- Two variants with different semantics ("relayed" vs "delivered") invite integration confusion; low-level call success is not semantic receiver acceptance.
- Retry is not refund: messages whose receivers can never succeed stay stuck without an application-level recovery path.
- Deleting payload hashes before receiver callbacks for reentrancy protection creates subtle retry-eligibility bugs when the callback reverts.
- Claims of non-blocking failure handling that lack `try/catch` or explicit failed state silently roll back pre-call markers — an easy audit miss.

## How It Works

There are two common variants. In execution-exact-once messengers, hash the versioned message envelope, mark success only after the destination call succeeds, and keep a separate failed marker for retry eligibility:

```solidity
function relayMessage(Message memory message) external {
    bytes32 messageHash = hashCrossDomainMessage(message);
    require(!successfulMessages[messageHash], "already relayed");
    require(_authenticatedSource(message), "bad source");

    (bool ok,) = message.target.call{gas: message.gasLimit}(message.data);
    if (ok) {
        successfulMessages[messageHash] = true;
        failedMessages[messageHash] = false;
    } else {
        failedMessages[messageHash] = true;
        revert("relay failed");
    }
}
```

Retry relays use the same message hash, not a new id, and must re-authenticate the source message before re-execution.

In delivery-first transports, delivery and execution are separated. The bridge marks the authenticated message as received before calling the destination application, then stores a failed-execution hash if the application call reverts or the destination code is missing:

```solidity
function receiveMessage(Message calldata message) external {
    bytes32 id = _messageId(message);
    require(!received[id], "already delivered");
    require(_authenticatedSource(message), "bad source");

    received[id] = true;
    if (!_tryExecute(message.target, message.gasLimit, message.payload)) {
        failedExecution[id] = keccak256(abi.encode(message));
    }
}

function retryExecution(Message calldata message) external {
    bytes32 id = _messageId(message);
    require(failedExecution[id] == keccak256(abi.encode(message)), "bad retry");
    delete failedExecution[id];
    require(_tryExecute(message.target, gasleft(), message.payload), "retry failed");
}
```

Delivery-first designs make relayer rewards depend on authenticated delivery, not application success. They need explicit wording that "received" does not mean the destination application accepted the payload.

For queued L1-to-L2 messages, retry can also mean replaying the same queued envelope with a larger gas limit. The replay path should read the original queue entry, recompute the original transaction hash using the old gas limit, and enqueue the same cross-domain calldata with the new gas limit only if the original queue element matches.

Low-level call success is not always semantic acknowledgement by the receiver.
If the destination can be an EOA or a contract with no return-value convention,
document whether delivery means "call did not revert" or "application-level
receiver acknowledged the message." Applications that need semantic acceptance
should make the receiver callback return or record an explicit acknowledgement.

## Key Points

- Bind message version, source chain, destination chain, nonce, sender, target, value, gas limit, and payload into the message hash.
- For execution-exact-once messengers, mark success after receiver execution and reject any later relay of the same successful hash.
- For delivery-first messengers, mark delivery before receiver execution, reject duplicate delivery, and track failed execution separately by full message hash.
- For gas-limit replay, authenticate the original queued envelope before accepting a new gas limit.
- Preserve failed-message state only as retry eligibility, not as proof that the message is safe.
- Scope temporary sender context to the relay call and clear it afterward.
- Document that retry is not the same as refund; receivers that can never succeed need an application-level recovery path.
- Distinguish low-level delivery success from semantic receiver acknowledgement.
- If the message id or payload hash is deleted before the receiver callback to prevent reentrancy, confirm whether a receiver revert restores the state and whether failed execution can be retried.
- Comments that claim failed application calls are non-blocking must be backed by `try/catch`, explicit failed-message state, or tests; otherwise a revert usually rolls back the pre-call marker.

## Source Evidence

- Optimism Bedrock's `CrossDomainMessenger` tracks successful and failed messages, uses versioned message hashes, sets temporary cross-domain sender context during relay, and tests retry-after-failure plus no-retry-after-success behavior.
- Polygon zkEVM/Agglayer treats low-level successful destination calls as delivered and permits EOA value delivery without application execution in [`contracts/AgglayerBridge.sol`](https://github.com/0xPolygonHermez/zkevm-contracts/blob/110bda5a03e70ee7331bc06407a8e79226d3e520/contracts/AgglayerBridge.sol).
- Mantle's legacy messenger verifies the original queue element and transaction hash before replaying the same L1-to-L2 cross-domain calldata with a new gas limit in [`packages/contracts/contracts/L1/messaging/L1CrossDomainMessenger.sol`](https://github.com/mantlenetworkio/mantle/blob/5cda5f811f73d9f331e6168617f87d3e19e6db6b/packages/contracts/contracts/L1/messaging/L1CrossDomainMessenger.sol).
- Avalanche ICM Teleporter marks messages received before destination execution, records failed execution hashes, and permits later `retryMessageExecution` in [`contracts/teleporter/TeleporterMessenger.sol`](https://github.com/ava-labs/icm-contracts/blob/0b68b03c906d17850712b49aa20f2dc18ed55568/contracts/teleporter/TeleporterMessenger.sol).
- LayerZero V2 stores verified inbound payload hashes, supports nilify and burn paths, and clears the exact payload hash before receiver callback in [`packages/layerzero-v2/evm/protocol/contracts/MessagingChannel.sol`](https://github.com/LayerZero-Labs/LayerZero-v2/blob/9c741e7f9790639537b1710a203bcdfd73b0b9ac/packages/layerzero-v2/evm/protocol/contracts/MessagingChannel.sol) and `EndpointV2.sol`.
- Across V3 tracks unfilled, requested slow fill, and filled relay statuses so a slow fill request can later be replaced by a fast fill while duplicate fills remain rejected in [`contracts/spoke-pools/SpokePool.sol`](https://github.com/across-protocol/contracts/blob/b4c4a46742dde83cbbace16ee066c6681b47ddee/contracts/spoke-pools/SpokePool.sol).
- Celer MessageBus stores message execution status, supports retry/fallback paths, and verifies transfer-with-message ids in [`contracts/message/messagebus/MessageBusReceiver.sol`](https://github.com/celer-network/sgn-v2-contracts/blob/b8a27161e0b700e30f30452c73418b60d133163f/contracts/message/messagebus/MessageBusReceiver.sol).
- Socket marks messages executed before proof and plug execution, but the plug call is not caught; failure rolls the marker back, so this is exact-once-on-success rather than a durable failed-message ledger in [`contracts/socket/SocketDst.sol`](https://github.com/SocketDotTech/socket-DL/blob/b2601e280533960df4d36eeef25ab81957f59eb9/contracts/socket/SocketDst.sol).

## Related Patterns

- [Chain-Bound Request Hash](./pattern-chain-bound-request-hash.md)
- [Canonical Bridge Counterpart Validation](./pattern-canonical-bridge-counterpart-validation.md)
- [Typed Cross-Chain Executor Options](./pattern-typed-cross-chain-executor-options.md)
- [Bridge Message Replay](../../ANTIPATTERNS.md#bridge-message-replay)
