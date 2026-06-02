# Batch 16 Findings

Batch 16 continues the expanded DefiLlama top-300 harvest after batch 15. It covers two canonical bridge / cross-chain messaging sources, one leveraged farming protocol, and one audit-report-only source.

## Sources Inspected

| Protocol | Repository | HEAD | Notes |
|----------|------------|------|-------|
| Mantle Bridge | `mantlenetworkio/mantle` | `5cda5f811f73d9f331e6168617f87d3e19e6db6b` | Legacy Optimism-style bridge and deployment authority pass. |
| Alpha Homora V2 | `AlphaFinanceLab/alpha-homora-v2-contract` | `f74fc460bd614ad15bbef57c88f6b470e5efd1fd` | Leveraged farming bank, wrappers, and oracle pass. |
| Avalon USDa | `avalonfinancexyz/USDa-audit-slowmist` | `d5b405bd1fc7cfcb16ea1dac42cb411909c3dff1` | Audit-report-only evidence; accepted items are caveated accordingly. |
| Avalanche ICM | `ava-labs/icm-contracts` | `0b68b03c906d17850712b49aa20f2dc18ed55568` | Teleporter messaging, registry, retry, and reward pass. |

## Accepted Catalog Updates

### Mantle Bridge

- Added [Fraud-Window Gated Message Finality](../../patterns/cross-chain/pattern-fraud-window-gated-message-finality.md) from Mantle's legacy state-root fraud-window and message-passer storage-proof withdrawal finality.
- Updated [Retryable Cross-Domain Message Ledger](../../patterns/cross-chain/pattern-retryable-cross-domain-message-ledger.md) with queued gas-limit replay that authenticates the original queue element before re-enqueueing the same calldata.
- Updated [Bootstrap Authority Handoff](../../patterns/access-control/pattern-bootstrap-authority-handoff.md) with code-hash checked temporary upgrade authority handoff.
- Updated [ANTIPATTERNS](../../ANTIPATTERNS.md) with EOA gates as a weak security boundary.

### Alpha Homora V2

- Added [Reward-Indexed ERC1155 Collateral Wrapper](../../patterns/lending/pattern-reward-indexed-erc1155-collateral-wrapper.md).
- Updated [Deferred Status Check Frame](../../patterns/lending/pattern-deferred-status-check-frame.md) with a spell-mediated lending frame.
- Updated [Action-Scoped Bounded Risk Prices](../../patterns/oracles/pattern-action-scoped-bounded-lending-prices.md) with token-specific borrow, collateral, and liquidation valuation factors.
- Updated [Conservative AMM LP Collateral Oracle](../../patterns/oracles/pattern-conservative-amm-lp-collateral-oracle.md) with fair-reserve LP valuation variants.
- Updated [Multi-Source Validation](../../patterns/oracles/pattern-multi-source-validation.md) with bounded 1-of-3 / 2-of-3 source agreement aggregation.
- Updated [Share-Denominated Lending Accounting](../../patterns/lending/pattern-share-denominated-lending-accounting.md) with borrow-share rounding discipline.
- Updated [ANTIPATTERNS](../../ANTIPATTERNS.md) with refund callbacks during temporary privileged execution contexts.

### Avalon USDa Audit

- Updated [Participant Permission Bitmap](../../patterns/access-control/pattern-participant-permission-bitmap.md) with one-sided negative tests for sender/receiver blocklist predicates.
- Updated [Delta NAV Share Accounting](../../patterns/vaults/pattern-delta-nav.md) with preview/execution accounting consistency and downstream precision minimums.
- Updated [Bounded Timelocked Parameter Change](../../patterns/access-control/pattern-bounded-timelocked-parameter-change.md) with hard upper bounds for claim, cooldown, and processing-period setters.
- Updated [Bounded Token Inflation](../../patterns/governance/pattern-bounded-token-inflation.md) and [ANTIPATTERNS](../../ANTIPATTERNS.md) to clarify that role or multisig gating is not enough for arbitrary mint/burn authority.
- Updated [Withdrawal Liquidity Buffer](../../patterns/vaults/pattern-withdrawal-liquidity-buffer.md) and [Operation Cadence Liveness Agent](../../patterns/monitoring/pattern-operation-cadence-liveness-agent.md) to distinguish funded claim reserves from operator top-up monitoring.

### Avalanche ICM

- Added [Receipt-Acknowledged Relayer Rewards](../../patterns/cross-chain/pattern-receipt-acknowledged-relayer-rewards.md).
- Added [Version-Gated Message Endpoint Registry](../../patterns/cross-chain/pattern-version-gated-message-endpoint-registry.md).
- Updated [Retryable Cross-Domain Message Ledger](../../patterns/cross-chain/pattern-retryable-cross-domain-message-ledger.md) with delivery-first retry semantics.
- Updated [Canonical Bridge Counterpart Validation](../../patterns/cross-chain/pattern-canonical-bridge-counterpart-validation.md) with same-address immutable messenger endpoint authentication.
- Updated [Deterministic Cross-Chain Factory](../../patterns/cross-chain/pattern-deterministic-cross-chain-factory.md) with same-address immutable messenger deployment as an authentication prerequisite.

## Rejected Or Deferred

- `LayerZero-Labs/usual-usd0-oft`, `ava-labs/evm-sgx-bridge`, and previously `aera-finance/aera-contracts-v3` were inaccessible or private during this pass and are not counted as inspected.
- Mantle's bridge-owned token pair, counterpart validation, escrow/refund, MNT handling, and global pause mechanics were rejected as already covered or too project-specific.
- Alpha Homora V2's native flash-loan README claim was rejected because the inspected implementation did not support it directly; EOA gating was captured as an anti-pattern, not a positive pattern.
- Avalon USDa staking and OFT-adapter ideas were rejected as audit-report-only and too protocol-specific for standalone pattern docs.
- Avalanche ICM replay protection, allowed-relayer lists, receiver validation, and Nick's method deployment were merged into existing cross-chain patterns instead of added as standalone pages.

## Contradictions Resolved

- Mantle's fraud-window finality was kept separate from dispute-game finality because the acceptance predicate differs.
- Avalanche ICM delivery-first semantics update the retryable message guidance without weakening execution-exact-once messengers; delivery and application execution are now explicitly separated.
- Avalon audit evidence is phrased as audit-source support, not production-proven positive evidence.
- EOA checks are cataloged as UX guardrails at best and anti-patterns when presented as security boundaries.
