# Batch 05 Findings

Dry-run analyses were run against 6 additional source repositories. This batch focused on Solana lending and AMMs, RWA async settlement, canonical bridges, proof-based exits, and cross-chain transport quorum.

## Source Repositories

| Protocol | Repository | Commit | Focus |
|----------|------------|--------|-------|
| Kamino Lend | `Kamino-Finance/klend` | `4c7653a` | Solana lending, elevation groups, liquidation priority, PDA authority, Token-2022 checks |
| Centrifuge Protocol | `centrifuge/liquidity-pools` | `e556c1a` | ERC-7540 RWA vaults, multi-adapter gateway quorum, spell authority, permissioned tranches |
| Raydium AMM | `raydium-io/raydium-amm` | `3b087ad` | Solana AMM, OpenBook inventory, bounded order cranks, account cohort checks |
| Arbitrum Bridge | `OffchainLabs/token-bridge-contracts` | `0746a71` | canonical bridge counterpart validation, retryable deployment, token registration, refund fallback |
| Polygon Bridge | `maticnetwork/pos-portal` | `3402faa` | checkpointed exits, root/child tunnels, predicate-mediated custody, migration cutover risk |
| Ondo Yield Assets | `code-423n4/2024-03-ondo-finance` | `4134cbe` | RWA redemption buffer and oracle variants from audit-contest snapshot; confidence downgraded |

## Accepted Catalog Updates

- Added cross-chain bridge patterns for canonical counterpart validation, checkpointed receipt exit proofs, authenticated root/child tunnels, predicate-mediated custody, multi-adapter message quorum, token-owned bridge registration, and escrow/mint-burn refund fallback.
- Added cross-chain requirements and risks for proof-bridge exit safety, bridge exit liveness, and migration cutover custody drain.
- Added Solana-specific authority and account-validation patterns for PDA-scoped protocol authority, account cohort validation, and instruction-paired flash loans.
- Added lending patterns for elevation-scoped borrow modes and risk-priority liquidation sequencing.
- Added liquidity patterns for orderbook-backed AMM inventory accounting, bounded cranked orderbook maintenance, and minimum liquidity locks.
- Updated existing docs with retryable deterministic deployment, bridge nullifier caveats, cross-chain bootstrap handoff, AMM operation-mode gating, ERC-7540 claim-ledger settlement, RWA request price ids, claim-ledger rounding, external minimum-lot redemption buffers, accepted-state oracle anchoring, action-scoped oracle flags, Token-2022 transfer-accounting checks, permissioned tranche variants, and risk-bearing ownership transfers.
- Expanded `ANTIPATTERNS.md` with stale-state bound checks, account role confusion, signature scope drift, bridge endpoint authentication mismatch, and hook replacement validation.

## Rejected Or Merged Candidates

- Plain async deposit/redeem queues, reserve caps, lazy accrual freshness, ordinary permission bitmaps, balance-delta transfers, oracle staleness checks, and generic replay ledgers were rejected as duplicates and merged only where a new variant existed.
- Raydium Fibonacci order spacing, Arbitrum WETH gateway details, Centrifuge trigger-redeem netting, Polygon deprecated ERC1155 chain-exit specifics, and Ondo cross-chain references outside the inspected source tree were rejected as project-specific or insufficiently evidenced.
- Ondo findings were treated as lower confidence because the source was a Code4rena audit-contest snapshot, not an official production repository.

## Contradiction Review

- Canonical bridge validation and checkpoint nullifiers were documented as narrower alternatives to application request hashes only when the bridge or checkpoint layer authenticates domain, peer, and replay.
- Bridge exit liveness keeps the existing `Pause Traps Funds` guidance but allows planned migration cutovers when a final source boundary, refund path, and custody accounting are explicit.
- Elevation groups are framed as constrained correlated-collateral isolation, not a blanket endorsement of correlated collateral baskets.
- Multi-adapter quorum is transport agreement, not complete replay protection; every adapter still needs endpoint and duplicate-message checks.
- Spell authority is constrained by delay, cancellation, manifest review, and separate pause authority so it does not normalize arbitrary governance execution.

## Verification

- Each source repository was inspected by a dry-run subagent using `skills/harvest-patterns/SKILL.md`.
- Existing catalog docs, `patterns/INDEX.md`, and `ANTIPATTERNS.md` were compared before accepting updates.
- Full catalog index regeneration and staged markdown validation were run before commit.
