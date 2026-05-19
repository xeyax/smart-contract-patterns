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

## Source Evidence

- Optimism Bedrock's `CrossDomainMessenger` tracks successful and failed messages, uses versioned message hashes, sets temporary cross-domain sender context during relay, and tests retry-after-failure plus no-retry-after-success behavior.
- Polygon zkEVM/Agglayer treats low-level successful destination calls as delivered and permits EOA value delivery without application execution in `/private/tmp/defillama-source/0xPolygonHermez__zkevm-contracts/contracts/AgglayerBridge.sol`.
- Mantle's legacy messenger verifies the original queue element and transaction hash before replaying the same L1-to-L2 cross-domain calldata with a new gas limit in `/private/tmp/defillama-source/mantlenetworkio__mantle/packages/contracts/contracts/L1/messaging/L1CrossDomainMessenger.sol`.
- Avalanche ICM Teleporter marks messages received before destination execution, records failed execution hashes, and permits later `retryMessageExecution` in `/private/tmp/defillama-source/ava-labs__icm-contracts/contracts/teleporter/TeleporterMessenger.sol`.

## Related Patterns

- [Chain-Bound Request Hash](./pattern-chain-bound-request-hash.md)
- [Canonical Bridge Counterpart Validation](./pattern-canonical-bridge-counterpart-validation.md)
- [Bridge Message Replay](../../ANTIPATTERNS.md#bridge-message-replay)
