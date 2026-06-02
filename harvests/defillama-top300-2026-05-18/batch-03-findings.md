# Batch 03 Findings

Dry-run analyses were run against 6 additional cloned repositories. This batch emphasized large lending systems, custody-routed minting, reward claims, queue exits, oracle-rate adapters, permissioning, and upgrade validation.

## Repositories Analyzed

| Protocol | Repository | Main Accepted Themes |
|----------|------------|----------------------|
| Aave | `aave-dao/aave-v3-origin` | reserve caps, scaled balances, reward indexes, L2 oracle sentinels |
| Morpho Blue | `morpho-org/morpho-blue` | isolated permissionless markets, share accounting, bad-debt realization |
| SparkLend | `sparkdotfi/sparklend-advanced` | benchmark rate adapters, peg monitors, exchange-rate valuation risk |
| ether.fi | `etherfi-protocol/smart-contracts` | consumer-scoped rate limits, delayed Merkle claims, serialized oracle reports |
| Ethena | `ethena-labs/bbp-public-assets` | custody-routed mint/redeem orders, break-glass limiters, bounded inflation |
| Maple Finance | `maple-labs/maple-core-v2` | permission bitmaps, credit-loss accounting, health checkers, upgrade paths |

## Catalog Changes Accepted

- Added access-control patterns for break-glass risk limiting, consumer-scoped token buckets, and participant permission bitmaps.
- Added custody/governance/monitoring patterns for signed custody-routed minting, bounded token inflation, and read-only protocol health checkers.
- Added lending patterns and requirements for reserve exposure caps, scaled balance tokens, bounded rate-source adapters, isolated permissionless markets, share-denominated accounting, explicit bad-debt realization, and credit-loss accounting.
- Added rewards patterns for lazy reward indexes and delayed cumulative Merkle claims.
- Added oracle docs for exchange-rate valuation risk and peg-ratio monitoring.
- Updated existing docs for withdrawal-buffer reserve predicates, async queue pricing caveats, ERC4626 reward vesting, selector-scoped call forwarding, serialized reporter execution, one-sided stablecoin caps, benchmark-targeted kinked rate curves, lending accounting freshness, L2 sequencer sentinels, oracle-jump buffers, version-gated upgrade paths, and permit front-run griefing.

## Rejected or Merged Candidates

- Lazy accrual, virtual share offsets, balance-delta transfers, two-step authority handoff, pause-scope findings, dead-share bootstraps, slippage bounds, and generic EIP-712 authorization were rejected as already covered.
- Ether.fi's call forwarding was merged into selector-scoped authority rather than becoming a separate pattern.
- Maple's cyclical withdrawal windows were treated as async queue evidence, not a standalone pattern.
- Morpho's permissionless singleton design was captured as a guarded isolated-market pattern and as anti-pattern caveats for shared pools and unguarded permissionless markets.
