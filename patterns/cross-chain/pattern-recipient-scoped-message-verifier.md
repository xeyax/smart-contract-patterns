# Recipient-Scoped Message Verifier

> Let each cross-chain message recipient choose its verifier while a generic mailbox enforces versioning, destination domain, and exact-once delivery.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, mailbox, recipient, verifier, ism |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A shared mailbox delivers messages for many applications
- Different recipients need different security modules or quorum rules
- The mailbox can enforce universal replay and destination checks
- Recipients can expose or register their verifier unambiguously

## Avoid When

- All recipients must use one global verifier for governance or compliance reasons
- Recipients can swap verifiers without delay, bounds, or monitoring
- The mailbox cannot authenticate origin, destination, nonce, and message body

## Trade-offs

**Pros:**
- Lets high-risk recipients require stronger verification than low-risk recipients
- Keeps generic delivery and replay logic in one mailbox
- Avoids hardcoding every application's verifier in the transport layer

**Cons:**
- Recipient verifier configuration becomes security-critical
- Weak recipient modules can still accept unsafe messages
- Integrators must understand verifier differences across recipients

## How It Works

The mailbox decodes the message, checks its version and destination domain,
derives a unique message id, and rejects duplicates. It then asks the recipient
which verifier to use and validates the message against that verifier before
calling the recipient.

```solidity
function process(bytes calldata metadata, bytes calldata message) external {
    require(message.version() == VERSION, "bad version");
    require(message.destination() == localDomain, "wrong domain");

    bytes32 id = message.id();
    require(!delivered[id], "delivered");

    address recipient = message.recipientAddress();
    IVerifier verifier = IRecipient(recipient).interchainSecurityModule();
    require(verifier.verify(metadata, message), "not verified");

    delivered[id] = true;
    IRecipient(recipient).handle(message.origin(), message.sender(), message.body());
}
```

## Implementation

- Mark the message delivered before or in the same protected frame as recipient execution.
- Bind version, nonce, origin domain, sender, destination domain, recipient, and body into the message id.
- Define fallback behavior when a recipient has no verifier.
- Treat verifier changes as critical governance or recipient-admin actions.
- Test wrong version, wrong destination, duplicate delivery, wrong verifier metadata, and recipient reverts.
- For plug or route-based recipients, bind the local recipient, remote sibling, inbound verifier, packet root, and executor policy in one route config.
- If the recipient chooses a threshold verifier policy, document whether the mailbox still owns replay protection or whether the recipient verifier must store its own consumed-message state.

## Source Evidence

- Hyperlane implements recipient-scoped verification in `/private/tmp/defillama-source/hyperlane-xyz__hyperlane-monorepo/solidity/contracts/Mailbox.sol` through `process` and `recipientIsm`.
- Hyperlane message encoding lives in `solidity/contracts/libs/Message.sol`.
- Hyperlane mailbox tests live in `solidity/test/Mailbox.t.sol`.
- Socket plug configuration binds local plug, sibling plug, inbound switchboard, outbound switchboard, capacitor, and decapacitor before packet-root execution in `/private/tmp/defillama-source/SocketDotTech__socket-DL/contracts/socket/SocketConfig.sol` and `SocketDst.sol`.
- Nomad routers enroll remote routers and reject messages from unenrolled remote senders before bridge-router handling in `/private/tmp/defillama-source/nomad-xyz__monorepo/packages/contracts-router/contracts/Router.sol` and `packages/contracts-bridge/contracts/BridgeRouter.sol`.

## Real-World Examples

- Hyperlane Mailbox lets recipients select their own interchain security module.

## Related Patterns

- [Multi-Adapter Message Quorum](./pattern-multi-adapter-message-quorum.md)
- [Route-Scoped DVN Quorum](./pattern-route-scoped-dvn-quorum.md)
- [Canonical Bridge Counterpart Validation](./pattern-canonical-bridge-counterpart-validation.md)
- [Bridge Endpoint Authentication Mismatch](../../ANTIPATTERNS.md#bridge-endpoint-authentication-mismatch)

## References

- Hyperlane Mailbox and ISM contracts.
