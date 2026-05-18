# Batch 02 Findings

Dry-run analyses were run against 6 additional cloned repositories. This batch emphasized custodial bridges, deterministic cross-chain deployment, selector-scoped operations, lending accounting, and reward streaming.

## Repositories Analyzed

| Protocol | Repository | Main Accepted Themes |
|----------|------------|----------------------|
| WBTC | `WrappedBTC/bitcoin-token-smart-contracts` | custodial mint/burn, reserve backing, request auditability |
| JustLend | `justlend/justlend-protocol` | lending accrual freshness, lazy borrow indexes, comptroller risk gates |
| Portal | `wormhole-foundation/wormhole-ntt-contracts` | deterministic cross-chain factories, bootstrap authority handoff, initialization latches |
| Spiko | `spiko-tech/contracts` | selector-scoped authority, allowlist transfers, redemption escrow, oracle history-depth checks |
| Convex Finance | `convex-eth/frax-cvx-platform` | user-owned proxy vaults, queued reward streaming, mutual parameter acceptance |
| cap | `cap-labs-dev/cap-contracts` | selector manifests, namespaced storage, dynamic imbalance premiums, fractional reserves |

## Catalog Changes Accepted

- Added access-control patterns for selector-scoped authority, bootstrap authority handoff, and mutual parameter acceptance.
- Added cross-chain patterns and requirements for custodial mint/burn, reserve backing, and deterministic cross-chain factories.
- Added lending patterns for accounting freshness, lazy borrow indexes, comptroller risk gates, and kinked utilization rate models.
- Added reward and token-integration patterns for queued reward streaming and balance-delta transfer accounting.
- Added upgrade and vault patterns for namespaced storage accessors and user-owned proxy vaults.
- Updated existing docs for clone deactivation, escrowed redemptions, investable withdrawal buffers, allocation imbalance premiums, Chainlink history-depth checks, anchor-capped oracle updates, donation-neutral wrappers, liquidation pause risk, and state initialization latches.

## Deferred Candidates

- Dust redemption operational DoS, state-coupled module replacement, transfer allowlist hooks, rate-limited operator escalation, target-health liquidation, and resetting Dutch auctions are promising but need more comparative evidence before becoming standalone pages.
- Some arbitrary execution, snapshot voting, proxy storage, and pause-scope findings were rejected as already covered by existing anti-patterns.
