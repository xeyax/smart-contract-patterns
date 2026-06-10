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

For OFT, native-mesh, or peer-configured bridges, treat lane activation as a
counterpart-validation event. Before enabling sends, verify both peer
directions, token or OFT linkage, executor and receive libraries, DVN or
verifier sets, enforced options, and block-confirmation policy for that route.

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
- Preflight route configuration in both directions before opening bridge sends.
- If using same-address endpoint authentication, document the deterministic deployment invariant and test wrong-origin-sender cases.
- For peer-configured messaging, validate both the local endpoint caller and the configured remote peer before trusting the payload.
- For token-bridge relayers, validate the canonical bridge's reported emitter or foreign contract before applying relayer-specific payload semantics.
- For cross-chain gauge or token bridges, keep root and leaf bridge counterpart configuration in the same deployment checklist as token, gauge, and voter wiring.

## Source Evidence

- Arbitrum token bridge gateways use `onlyCounterpartGateway` checks on both L1 and L2 finalize paths.
- `L1ArbitrumMessenger.getL2ToL1Sender` recovers the remote L2 sender from the active bridge/outbox context.
- Foundry tests reject non-bridge callers, wrong counterpart gateways, and missing outbox sender context.
- Optimism Bedrock standard bridges validate the local messenger and the remote bridge sender, while L2 messenger paths normalize L1-to-L2 address aliasing before accepting the counterpart.
- Avalanche ICM Teleporter requires Warp messages to report `originSenderAddress == address(this)` and documents same-address universal deployment for `TeleporterMessenger` in [`contracts/teleporter/TeleporterMessenger.sol`](https://github.com/ava-labs/icm-contracts/blob/0b68b03c906d17850712b49aa20f2dc18ed55568/contracts/teleporter/TeleporterMessenger.sol) and `contracts/teleporter/README.md`.
- Sophon's custom USDC bridge authenticates Bridgehub, chain-scoped L2 bridge addresses, L1-to-L2 alias normalization on L2, and L2 sender proofs on withdrawal finalization in [`src`](https://github.com/sophon-org/custom-usdc-bridge/blob/72b36f11fb6c901380836043a43c738c434d5c12/src).
- USDT0 deployment audit reports repeatedly check bidirectional LayerZero peer, DVN, executor, library, enforced-option, and confirmation configuration before activation; this is audit-source evidence, not code-proven behavior from this repository.
- LayerZero V2 OApps require calls from the local endpoint and reject messages whose origin sender is not the configured peer in [`packages/layerzero-v2/evm/oapp/contracts/oapp/OAppReceiver.sol`](https://github.com/LayerZero-Labs/LayerZero-v2/blob/9c741e7f9790639537b1710a203bcdfd73b0b9ac/packages/layerzero-v2/evm/oapp/contracts/oapp/OAppReceiver.sol) and `OAppCore.sol`.
- Wormhole's token bridge relayer registers foreign contracts and rejects transfers whose emitter does not match the registered source in [`evm/src/token-bridge-relayer/TokenBridgeRelayerGovernance.sol`](https://github.com/wormhole-foundation/example-token-bridge-relayer/blob/b8ac43d008f9867193e8d08bc54211ae4f5803df/evm/src/token-bridge-relayer/TokenBridgeRelayerGovernance.sol) and `TokenBridgeRelayer.sol`.
- Velodrome Superchain root and leaf token/message bridges bind counterpart bridge roles across [`src/root/bridge`](https://github.com/velodrome-finance/superchain-contracts/blob/c93c466a2fcd1fd9dc79ba569f6b81c42bb50d61/src/root/bridge) and [`src/bridge`](https://github.com/velodrome-finance/superchain-contracts/blob/c93c466a2fcd1fd9dc79ba569f6b81c42bb50d61/src/bridge).

## Related Patterns

- [Chain-Bound Request Hash](./pattern-chain-bound-request-hash.md)
- [Authenticated Root-Child Tunnel](./pattern-authenticated-root-child-tunnel.md)
- [Retryable Cross-Domain Message Ledger](./pattern-retryable-cross-domain-message-ledger.md)
- [Route-Scoped Message Library Migration](./pattern-route-scoped-message-library-migration.md)
- [Bridge Message Replay](../../ANTIPATTERNS.md#bridge-message-replay)
