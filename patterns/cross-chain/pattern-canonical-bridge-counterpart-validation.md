# Canonical Bridge Counterpart Validation

> Authenticate both the canonical bridge messenger and the remote application counterpart before finalizing cross-chain messages.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, messenger, counterpart, rollup, authentication |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | High |

## Use When

- Application contracts receive messages through a canonical rollup or bridge messenger
- Replay protection and source-domain binding are provided by the bridge layer
- The receiving contract still needs to know which remote application sent the message
- Both L1-to-L2 and L2-to-L1 paths are supported

## Avoid When

- The bridge cannot authenticate the remote sender or source domain
- Messages are relayed by arbitrary executors without a canonical messenger context
- The application already verifies full source proofs directly

## Trade-offs

**Pros:**
- Separates bridge-layer authenticity from application-layer authorization
- Prevents valid bridge messages from the wrong remote contract from finalizing
- Keeps application replay logic smaller when the canonical bridge already provides it

**Cons:**
- Safety depends on the canonical bridge's replay and domain guarantees
- Messenger APIs differ across rollups and can be easy to misuse
- Upgrades must preserve counterpart configuration on both domains

## How It Works

The receiver checks two identities:

1. The local caller is the canonical bridge messenger or active outbox/inbox.
2. The remote sender recovered from the bridge context equals the configured counterpart.

```solidity
function finalize(bytes calldata payload) external {
    require(msg.sender == canonicalMessenger, "wrong messenger");
    require(_remoteSender() == counterpartGateway, "wrong counterpart");

    _finalize(payload);
}
```

For bridges that alias L1 senders on L2, normalize through the bridge's official sender-recovery primitive instead of comparing raw `msg.sender`.

Some transports deliberately deploy the same immutable messenger bytecode to the
same address on every chain. In that model, the local endpoint can authenticate
the remote endpoint by requiring the bridge-provided origin sender to equal
`address(this)`, but only if deployment tooling proves the same-address,
same-bytecode invariant and message ids are still bound to source and
destination domains.

## Key Points

- Validate messenger and counterpart on every finalize path.
- Treat bridge sender-recovery calls as part of the trusted boundary and test their failure modes.
- Reject messages from the default gateway, router, or owner unless that exact address is the configured peer.
- Do not use this pattern as a substitute for bridge-layer replay protection.
- Include counterpart updates in governance, deployment, and migration playbooks.
- If using same-address endpoint authentication, document the deterministic deployment invariant and test wrong-origin-sender cases.

## Source Evidence

- Arbitrum token bridge gateways use `onlyCounterpartGateway` checks on both L1 and L2 finalize paths.
- `L1ArbitrumMessenger.getL2ToL1Sender` recovers the remote L2 sender from the active bridge/outbox context.
- Foundry tests reject non-bridge callers, wrong counterpart gateways, and missing outbox sender context.
- Optimism Bedrock standard bridges validate the local messenger and the remote bridge sender, while L2 messenger paths normalize L1-to-L2 address aliasing before accepting the counterpart.
- Avalanche ICM Teleporter requires Warp messages to report `originSenderAddress == address(this)` and documents same-address universal deployment for `TeleporterMessenger` in `/private/tmp/defillama-source/ava-labs__icm-contracts/contracts/teleporter/TeleporterMessenger.sol` and `contracts/teleporter/README.md`.

## Related Patterns

- [Chain-Bound Request Hash](./pattern-chain-bound-request-hash.md)
- [Authenticated Root-Child Tunnel](./pattern-authenticated-root-child-tunnel.md)
- [Retryable Cross-Domain Message Ledger](./pattern-retryable-cross-domain-message-ledger.md)
- [Bridge Message Replay](../../ANTIPATTERNS.md#bridge-message-replay)
