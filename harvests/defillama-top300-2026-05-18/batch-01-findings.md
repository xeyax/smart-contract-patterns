# Batch 01 Findings

Dry-run analyses were run against the first 12 cloned repositories. The catalog updates below were accepted because they were reusable across protocol designs or sharpened existing anti-pattern guidance.

## Repositories Analyzed

| Protocol | Repository | Main Accepted Themes |
|----------|------------|----------------------|
| Lido | `lidofinance/core` | bounded async withdrawal finalization, pause/claim liveness |
| EigenCloud | `Layr-Labs/eigenlayer-contracts` | virtual share offsets, delayed withdrawal/slashing liability |
| Pendle | `pendle-finance/pendle-core-v2-public` | TWAP readiness, Chainlink-compatible wrappers, callback trust |
| Veda | `Veda-Labs/boring-vault` | off-chain NAV bounds, transfer hooks, multi-asset accounting |
| Symbiotic | `symbioticfi/core` | actual-received deposits, epoch withdrawal liability, bounded hooks |
| Enzyme Finance | `enzymefinance/protocol` | async batch settlement, Chainlink-compatible rate adapters |
| Renzo | `Renzo-Protocol/contracts-public` | withdrawal liquidity buffers, cross-chain price guardrails, oracle shim staleness |
| Beefy | `beefyfinance/beefy-contracts` | locked profit smoothing, exit-preserving emergency unwind, swap template validation |
| Nexus Mutual | `NexusMutual/smart-contracts` | dynamic max-cost/deadline bounds, Chainlink staleness caveats |
| Reserve Protocol | `reserve-protocol/reserve-index-dtf` | bounded rebalance auctions, delayed unstaking, version-gated upgrades |
| Rocket Pool | `rocket-pool/rocketpool` | threshold reporter consensus, public queue settlement, authority handoff |
| Function FBTC | `fbtc-xyz/fbtc-contract` | chain-bound bridge request hashes, destination-chain validation, finality/refund risks |

## Catalog Changes Accepted

- Added new patterns for virtual share offsets, locked profit smoothing, withdrawal liquidity buffers, bounded rebalance auctions, threshold reporter consensus, chain-bound request hashes, two-step authority handoff, and version-gated upgrade registries.
- Updated oracle docs with TWAP readiness gates, Chainlink-compatible wrapper caveats, `latestAnswer()` staleness risk, rate-limited accepted-state updates, and reporter-quorum centralization assumptions.
- Updated vault docs with actual-received accounting, public gas-bounded queue settlement, withdrawal buffer refills, delayed unstaking, emergency exit liveness, and utilization-based withdrawal fees.
- Updated upgrade/factory docs with scoped beacon cohorts, deterministic beacon proxy trade-offs, and required post-upgrade tests.
- Updated anti-patterns with concrete variants for pause trapping claims/refunds, fee-on-transfer accounting, hook/callback binding, bridge replay domains, decimal rejection, admin-bounded modules, donation griefing, swap route templates, governance vote locks, and beacon blast-radius control.

## Deferred Candidates

- Cross-chain finality and refund/cancel risks deserve dedicated `risk-*` docs after more bridge repos are inspected.
- Sub-oracle registries, parser-gated external positions, immutable custody vaults, lazy bucket expiration, vote-lock governance, and instance-owned delegate upgrades are promising but should be compared against more repos before adding standalone pages.
- Some project-specific mechanisms were rejected as too local or already covered by existing docs.
