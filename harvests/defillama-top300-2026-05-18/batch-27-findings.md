# Batch 27 Findings

## Source Repositories

| Protocol | Repository | Commit | Focus |
|----------|------------|--------|-------|
| Across | `across-protocol/contracts` | `b4c4a46742dde83cbbace16ee066c6681b47ddee` | Fast/slow fills, bonded root bundles |
| Hop Protocol | `hop-protocol/contracts` | `0726ffa0e14745134116e552178fd7e0edcfa8e6` | Bonded transfer roots |
| LayerZero V2 | `LayerZero-Labs/LayerZero-v2` | `9c741e7f9790639537b1710a203bcdfd73b0b9ac` | Message libraries, ULN, executor options |
| deBridge | `debridge-finance/debridge-contracts-v1` | `2e9f9c73438738310b5293cec4cffe25741e9b1f` | Submission ids, oracle confirmations, auto calls |
| Connext | `connext/monorepo` | `7758e62037bba281b8844c37831bde0b838edd36` | Aggregate roots, fast liquidity, reconciliation |
| Celer SGN | `celer-network/sgn-v2-contracts` | `b8a27161e0b700e30f30452c73418b60d133163f` | Signer quorum, delayed payouts, message bus |
| Synapse | `synapsecns/synapse-contracts` | `60f1c25cf2f115911e11255f515e1450fe96100c` | RFQ router, legacy bridge/message risks, stable AMM |
| LI.FI | `lifinance/contracts` | `02e19af066bbbd3ea8e9e93112ccae74636487b4` | Swap allowlists, bridge calldata validation, receivers |
| Socket | `SocketDotTech/socket-DL` | `b2601e280533960df4d36eeef25ab81957f59eb9` | Plug routes, switchboard roots, capacitor guardrails |
| Wormhole Relayer Example | `wormhole-foundation/example-token-bridge-relayer` | `b8ac43d008f9867193e8d08bc54211ae4f5803df` | Foreign contract validation, native drops |
| Stargate V1 | `stargate-protocol/stargate` | `c4212c2ee76997b1099ee9b34da0f1ed32dcf9c4` | Cached swaps, shared liquidity, retry/revert |
| Nomad | `nomad-xyz/monorepo` | `b64c5aebbdc3d9fc8416ab1d18f93ea5b00f0411` | Replica roots, router peers, recovery accounting |

`router-protocol/router-chain` and `decentxyz/box` were unavailable during this
batch and are not counted.

## Accepted Catalog Updates

- Added [Route-Scoped Message Library Migration](../../patterns/cross-chain/pattern-route-scoped-message-library-migration.md), [Route-Scoped DVN Quorum](../../patterns/cross-chain/pattern-route-scoped-dvn-quorum.md), [Typed Cross-Chain Executor Options](../../patterns/cross-chain/pattern-typed-cross-chain-executor-options.md), [Threshold-Delayed Bridge Payout](../../patterns/cross-chain/pattern-threshold-delayed-bridge-payout.md), and [Relayer-Funded Native Drop Accounting](../../patterns/cross-chain/pattern-relayer-funded-native-drop-accounting.md).
- Updated cross-chain replay, exact-once message, domain-root, optimistic batch, counterpart-validation, recipient-verifier, refund, exit-liveness, rate-limit, and versioning guidance with evidence from Across, Hop, LayerZero, deBridge, Connext, Celer, Socket, Wormhole, Stargate, LI.FI, and Nomad.
- Updated selector-scoped authority, registry-routed recipe, and swap-router guidance for LI.FI-style contract-selector allowlists and approve-only spenders.
- Updated anti-pattern guidance for stale-state bound checks, bridge zero-root initialization, external DVN confirmation drift, bridge calldata parser drift, gas-packed validation bypass, bridged arbitrary governance execution, and bridge fee-on-transfer onboarding assumptions.

## Rejected Or Deferred Candidates

- Synapse FastBridge was rejected as a positive pattern because the inspected checkout exposed mostly interfaces and tests, not the production lifecycle implementation.
- Synapse legacy nodegroup bridge and MessageBus receiver findings were merged as anti-pattern variants rather than positive patterns because they concentrate trust or rely on executor-supplied ids.
- LayerZero external bridge DVN adapters were rejected as a positive verifier pattern because the inspected adapter base deliberately does not preserve the configured block-confirmation policy.
- deBridge value-and-surge validator confirmation escalation was deferred as a standalone pattern; this batch captured the stronger reusable parts through route-scoped quorum, chain-bound ids, and admin-risk caveats.
- Nomad incident recovery receipts were merged into exit-liveness guidance rather than promoted to a new pattern because the recovery-accounting surface is still incident-specific.
- Stable AMM invariant evidence from Synapse and shared-liquidity evidence from Stargate were treated as support for existing liquidity docs, not new bridge-specific patterns.

## Contradictions And Caveats

- Route-scoped library migration is distinct from endpoint-version gating: the endpoint address can stay fixed while old and new receive libraries overlap during a grace window.
- Route-scoped DVN quorum is not the same as a stake-backed DVN adapter. The former is route policy; the latter is one external verifier implementation.
- Threshold-delayed payouts delay validator-approved transfers after approval. They do not prove source-chain finality.
- Relayer-funded native drops do not create receipt-acknowledged relayer rewards; they split redemption, native funding, fees, and refunds on the destination side.
- Socket's execution marker is set before plug execution but rolls back on revert, so it is exact-once-on-success rather than a durable failed-message ledger.
- Nomad zero-root fixes are captured as regression guardrails; the production initializer is guarded even though harnesses can force legacy state for tests.
