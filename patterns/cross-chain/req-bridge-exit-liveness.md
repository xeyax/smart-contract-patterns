# Bridge Exit Liveness Requirements

> Requirements that keep already-escrowed, burned, or proven bridge assets claimable through pauses, failures, and migrations.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, liveness, pause, refund, migration |
| Type | Requirement |

## R1: Pauses Preserve Safe Exit Paths

**Pausing new bridge inflows should not automatically pause withdrawals, refunds, or already-proven exits.**

### What This Means

- Deposit pause and exit pause are separate controls.
- Directional bridge pauses are preferable: pausing sends in one direction should not automatically block opposite-direction claims.
- If all exits cannot remain open, the safest solvent exit path stays available.
- Emergency playbooks explain when and why an exit pause can be used.

## R2: Failed Destination Settlement Has A Refund Path

**If a destination token, peer, or gateway validation fails, users can recover source value through an authenticated refund path.**

### What This Means

- Destination finalization fails closed instead of minting into invalid mappings.
- Refund messages are replay-safe and authenticated by the bridge.
- Refunds remain callable while new deposits are paused.
- Sending failed settlement funds to an admin or multisig is not a user refund path unless on-chain entitlement and claim semantics define how users recover funds.
- Split value-transfer/routing-metadata flows need recovery when value is attested or delivered but the metadata sidecar is delayed, malformed, missing, or unpaired.
- Deposit cancellation or reclaim must bind the exact message envelope and document non-refundable messaging fees.
- Compose or multihop bridges need explicit failed-message state, retry/refund semantics, and reserved gas or value rules so a malformed second-hop payload does not strand the first-hop value.
- Fast-liquidity bridges need a slow-fill, canonical-fill, or refund path for deposits that are not competitively filled before their deadline.
- Delayed large payouts need a public post-delay executor and a pause policy that does not permanently trap already-approved transfers.

## R3: Migration Accounts For In-Flight Messages

**Bridge migration must account for pending retryables, proofs, exits, and delayed messages before burning escrow or removing mint authority.**

### What This Means

- Operators define a final accepted source boundary.
- Pending messages are completed, refunded, or made claimable elsewhere.
- Custody or mint authority moves only after the old bridge's obligations are bounded.
- Migration playbooks account for routers, legacy message formats, pending batched messages, liquidity buffers, and direct-route failure modes.
- Cutovers should pause new sends, drain in-flight batches, clear route credits, update roles, and revalidate accounting invariants before reconnecting.

## R4: Admin Overrides Are Explicitly Trusted

**Owner or governance override paths that can force registration, burn custody, or move bridge roles must be documented as trusted paths.**

### What This Means

- Override events include token, gateway, peer, and amount fields.
- Monitoring can detect changes that strand pending exits.
- Tests cover override misuse around in-flight settlement.

## R5: Emergency Exit Pauses Are Scoped And Expiring

**A bridge that must pause proof or exit finalization needs narrow identifiers, expiry, monitoring, and a documented reason why no safer exit path can remain open.**

### What This Means

- Pause identifiers distinguish deposits, proof submission, finalization, and lockbox movement.
- Exit pauses have maximum duration or explicit renewal procedures.
- Users know whether timed-out redemptions, refunds, or standard proof-based exits remain callable.
- If an emergency mode blocks both sends and claims, document it as a trusted break-glass exception rather than as normal liveness-preserving pause design.

## Source Evidence

- Arbitrum token bridge pauses deposits while preserving L1 withdrawal finalization paths.
- Arbitrum gateway fallback handlers issue refund withdrawals when destination token validation fails.
- Arbitrum native USDC migration tests check pending deposits before burn and role transfer.
- Optimism Bedrock uses scoped pause identifiers with expiry, but paused portal proof and finalization paths remain liveness exceptions that need operational justification.
- tBTC v2 redemptions include timeout paths that restore balances or keep timed-out redemptions honor-able, and optimistic mint pauses do not block standard proof-based minting.
- Tornado Nova's failed external settlement path shows why admin recovery of funds should not be treated as equivalent to user-claimable bridge refund semantics.
- Noble's CCTP metadata wrapper shows a split value-transfer and routing-metadata flow where liveness depends on pairing the sidecar metadata with the canonical value message.
- StarkGate shows delayed, depositor-only reclaim for exact bridge message envelopes, with the caveat that the remote message can still be consumed before reclaim and fees may remain spent.
- Linea message service tests show directional pause behavior where sends and claims can be paused independently in [`contracts/test/hardhat/messaging/l1/L1MessageService.ts`](https://github.com/Consensys/linea-monorepo/blob/1f6880839cd2dff45009ccd9bffef0e68b0bb2f3/contracts/test/hardhat/messaging/l1/L1MessageService.ts).
- Gnosis xDAI bridge USDS migration docs and tests cover router compatibility, legacy message handling, direct-route failure cases, and liquidity buffers for claims in [`USDSMigration.md`](https://github.com/gnosischain/tokenbridge-contracts/blob/52afd25b05f1afa3347f2f18595748b2149df6aa/USDSMigration.md) and bridge tests.
- Stargate V2 migration tests pause new sends, drain buses, clear credits, revoke mint authority, burn locked supply or credit, reconnect pools, and revalidate invariants in [`packages/stg-evm-v2/test/stargatePoolMigratable/OFTPoolToPoolMigrationTest.t.sol`](https://github.com/stargate-protocol/stargate-v2/blob/8c41a9670d1b7d910862826829e44a23aa1afea0/packages/stg-evm-v2/test/stargatePoolMigratable/OFTPoolToPoolMigrationTest.t.sol).
- Polygon zkEVM/Agglayer emergency mode can block bridge sends and claim finalization in [`contracts/AgglayerBridge.sol`](https://github.com/0xPolygonHermez/zkevm-contracts/blob/110bda5a03e70ee7331bc06407a8e79226d3e520/contracts/AgglayerBridge.sol), illustrating a broad break-glass exception that must be operationally justified.
- USDT0 multihop, native-mesh, and deployment audit reports repeatedly discuss composed-message retry/refund handling, malformed payload recovery, and lane preflight checks; these are lower-confidence audit-source examples because the source repository inspected here contains reports, not implementation code.
- Across V3 exposes slow-fill requests and slow-fill Merkle proof execution when fast relayers do not fill a deposit in [`contracts/spoke-pools/SpokePool.sol`](https://github.com/across-protocol/contracts/blob/b4c4a46742dde83cbbace16ee066c6681b47ddee/contracts/spoke-pools/SpokePool.sol).
- Stargate V1 caches failed destination swaps and exposes retry or revert paths in [`contracts/Router.sol`](https://github.com/stargate-protocol/stargate/blob/c4212c2ee76997b1099ee9b34da0f1ed32dcf9c4/contracts/Router.sol).
- Celer SGN bridge and pool delay large approved payouts above token thresholds, with public delayed execution after the delay in [`contracts/safeguard/DelayedTransfer.sol`](https://github.com/celer-network/sgn-v2-contracts/blob/b8a27161e0b700e30f30452c73418b60d133163f/contracts/safeguard/DelayedTransfer.sol), `contracts/liquidity-bridge/Bridge.sol`, and `contracts/liquidity-bridge/Pool.sol`.
- LI.FI destination receivers catch failed compose execution and refund remaining assets to the receiver or fallback path in [`src/Periphery/ReceiverStargateV2.sol`](https://github.com/lifinance/contracts/blob/7aeb2419d52d6bf834bf2c47e54dd8ea470a57bd/src/Periphery/ReceiverStargateV2.sol) and `src/Periphery/ReceiverAcrossV4.sol`.
- Nomad recovery accountants record affected bridge assets and expose pro-rata claim accounting in [`packages/contracts-bridge/contracts/BridgeRouter.sol`](https://github.com/nomad-xyz/monorepo/blob/b64c5aebbdc3d9fc8416ab1d18f93ea5b00f0411/packages/contracts-bridge/contracts/BridgeRouter.sol) and accountant contracts.

## Related Patterns

- [Escrow Mint-Burn Refund Fallback](./pattern-escrow-mint-burn-refund-fallback.md)
- [Proof Bridge Exit Safety Requirements](./req-proof-bridge-exit-safety.md)
- [Retryable Cross-Domain Message Ledger](./pattern-retryable-cross-domain-message-ledger.md)
- [Threshold-Delayed Bridge Payout](./pattern-threshold-delayed-bridge-payout.md)
- [Relayer-Funded Native Drop Accounting](./pattern-relayer-funded-native-drop-accounting.md)
- [Pause Traps Funds](../../ANTIPATTERNS.md#pause-traps-funds)
