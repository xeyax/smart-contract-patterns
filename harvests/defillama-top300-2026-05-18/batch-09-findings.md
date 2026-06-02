# Batch 09 Findings

Dry-run analyses were run against 8 additional source candidates. This batch had several strong matches, plus two category mismatches that still yielded useful AMM or crypto-boundary evidence.

## Source Repositories

| Protocol | Repository | Commit | Focus |
|----------|------------|--------|-------|
| Dolomite | `dolomite-exchange/harvest-strategy-arbitrum` | `b7b4387` | leveraged yield router over shared margin core |
| Noble Chain | `noble-assets/cctp-contracts` | `2bc70b1` | CCTP value transfer plus routing metadata sidecar |
| Stake DAO | `stake-dao/contracts-monorepo` | `73fa29b` | epoch fee buckets, collateral wrappers, LP collateral oracles |
| Doppler Finance | `girin-app/contracts` | `111e3a2` | Venus/Compound-derived lending caveats; weak brand match |
| Lagoon | `hopperlabsxyz/lagoon-v0` | `37a84cb` | ERC-7540 vaults, NAV guardrails, opt-in proxy upgrades |
| Railgun | `Railgun-Community/curve25519-scalarmult-wasm` | `20aac34` | Rust/WASM crypto utility; rejected for catalog updates |
| Loopscale | `LoopscaleLabs/damm-v2` | `f95a5d4` | Meteora DAMM v2 AMM; category mismatch for lending |
| infiniFi | `InfiniFi-Labs/infinifi-protocol` | `3f0e186` | yield smoothing, tiered loss waterfalls |

## Accepted Catalog Updates

- Added new docs for checkpointed epoch reward buckets, yield-preserving collateral wrappers, conservative AMM LP collateral oracles, rate-bounded NAV reports, volatility-accumulator dynamic fees, extension-gated Token-2022 transfer-fee normalization, and tiered loss-waterfall requirements.
- Updated shared-liquidity kernel guidance with Dolomite-style leveraged router callback boundaries.
- Updated lazy reward index guidance with external-margin ledger checkpointing and terminal emission cursors.
- Updated dust liquidation guidance with full-account dust healing and explicit bad-debt realization links.
- Updated timelocked parameter changes with delay-reduction bypass guardrails.
- Updated chain-bound request hashes and bridge liveness requirements with Noble-style value-transfer plus routing-metadata sidecars.
- Updated async vault docs with ERC-7540 settlement snapshots and hybrid sync/async NAV-validity caveats.
- Updated version-gated upgrade docs with Lagoon-style per-instance timelocked opt-in upgrades and fail-open registry caveats.
- Updated locked-profit smoothing with infiniFi fixed-maturity value smoothing.
- Expanded anti-pattern guidance for loop-bound/cardinality mismatches and decimal-normalization underflow.

## Rejected Or Merged Candidates

- Railgun's `curve25519-scalarmult-wasm` repo was rejected for catalog updates because it is an off-chain Rust/WASM helper rather than smart-contract, circuit, or protocol source.
- Loopscale's source-map row was a lending mismatch; its AMM evidence was accepted only for liquidity and token-integration docs.
- Dolomite's leveraged farming router was merged into shared-liquidity and callback guidance rather than added as a standalone strategy pattern.
- Noble's CCTP wrapper was merged into sidecar metadata guidance rather than added as a project-specific bridge pattern.
- Stake DAO router delegatecall and Permit2 material was rejected as already covered by wallet recipe, approval persistence, and delegatecall context guidance.
- infiniFi redemption queue and gateway zap findings were merged into existing async withdrawal and slippage anti-pattern docs.

## Contradiction Review

- Shared-liquidity warnings remain valid; Dolomite is framed as a controlled exception only under core callback authentication, receipt-token checks, and user slippage/deadline enforcement.
- CCTP sidecar metadata does not replace canonical bridge identity; it must commit to the canonical value-message nonce or id.
- Conservative LP oracles are not treated as market-clearing prices and still carry exchange-rate valuation risk.
- Token-2022 fee normalization is a narrow deterministic-extension case, not arbitrary fee-on-transfer token support.
- Tiered loss waterfalls are intentionally not pro-rata fairness; they require explicit opt-in senior/junior risk classes.

## Verification

- Each source repository was inspected by a dry-run subagent using `skills/harvest-patterns/SKILL.md`.
- Existing catalog docs, `patterns/INDEX.md`, and `ANTIPATTERNS.md` were compared before accepting updates.
- Category mismatches were documented and constrained to the domains evidenced by the code.
- Full catalog index regeneration and staged markdown validation were run before commit.
