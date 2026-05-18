# Batch 07 Findings

Dry-run analyses were run against 8 additional source repositories. This batch focused on veto governance, permissioned RWA tokens, bridged staking rates, shielded-pool accounting, relay validator sets, BNB liquid staking, and user-wallet automation.

## Source Repositories

| Protocol | Repository | Commit | Focus |
|----------|------------|--------|-------|
| Lido Dual Governance | `lidofinance/dual-governance` | `ba9dfc9` | stakeholder veto, rage quit, deadlock recovery |
| Spiko Stellar | `spiko-tech/stellar-contracts` | `776ed77` | permissioned token roles, idempotent operations, redemptions |
| Veda Plasma | `Veda-Labs/boring-vault-plasma` | `1b3501b` | Merkle manager permissions, solver withdrawal queues, bridge rate limits |
| Rocket Pool Polygon Oracle | `rocket-pool/rocketpool-polygon-oracle` | `8be9f3c` | permissionless bridged source-rate relay, child tunnel dispatch |
| Tornado Nova | `tornadocash/tornado-nova` | `f9264ee` | shielded-pool accounting, root history, ext-data binding |
| Symbiotic Relay | `symbioticfi/relay-contracts` | `cba7181` | epoch headers, key registry, voting-power calculators |
| Stader BNBx | `stader-labs/bnbX` | `18442f8` | BNB liquid-staking share, operator registry, withdrawal batches |
| Defi Saver V3 | `defisaver/defisaver-v3-contracts` | `5bacdcc` | wallet automation recipes, strategy subscriptions, registries |

## Accepted Catalog Updates

- Added governance docs for stakeholder-extensible timelocks, local rage-quit settlement, condition-gated tiebreakers, proposal-embedded execution guards, veto liveness requirements, supply-reference drift, exit-dependent deadlocks, epoch validator-set headers, composable voting-power calculators, and chain voting-power concentration risk.
- Added automation and routing docs for registry-routed wallet recipes, hash-anchored strategy subscriptions, changeable trigger gates, wallet-native auth adapters, timelocked address registries, and registry-gated exchange fallback.
- Added zero-knowledge docs for shielded-pool accounting invariants, bounded Merkle root history, and circuit-bound external settlement hashes.
- Added oracle, token, vault, and monitoring docs for permissionless bridged source-rate relays, timeboxed idempotency keys, operator-routed LST shares, curated validator registries, exchange-rate-preserving LST cutovers, and operation cadence liveness agents.
- Updated existing docs for Merkle permission manifests, role-backed participant eligibility, pairwise bridge rate limits, self-dispatched tunnel payloads, bridged-rate source freshness, exchange-rate valuation, LST accepted-state bounds, async solver queues, pending-exit parameter drift, bounded FIFO withdrawal batches, share-lock parameter drift, bridge refund semantics, and global-vs-local settlement boundaries.
- Expanded `ANTIPATTERNS.md` with prose-only security guardrails, fixed-window revocation blind spots, unkeyed transient execution context, temporary flash-loan permission caveats, permissioned exit custody clarification, relay view aggregation caveats, and governance deadlock wording.

## Rejected Or Merged Candidates

- Reporter consensus, exchange-rate valuation, bridge authentication, selector scoping, participant eligibility, and bounded queue findings were merged into existing docs where the catalog already had the base pattern.
- Veda Merkle roots were not treated as inherently timelocked; the accepted update is about selector/argument-scoped manifests.
- Rocket Pool's bridged rate provider was not treated as threshold consensus because relay submission is permissionless and bridge-authenticated, not multi-reporter voting.
- Stader exchange-rate bounds were not presented as market-price safety; they constrain internal LST accounting only.
- Defi Saver transient storage findings were documented as keyed-context guidance, not as a blanket rejection of transient storage.

## Contradiction Review

- Local rage quit remains distinct from global settlement because it isolates a dispute cohort instead of settling all liabilities.
- Deadlock tiebreakers are not break-glass risk limiters: they can resume or reseal systems, so their safety depends on objective conditions and narrow powers.
- Destination bridge execution timestamps are not source freshness timestamps for rate providers.
- Stable cross-chain signature domain substitutes are acceptable only when they explicitly bind the replay boundary and verifier context.
- Permissioned redemption records improve traceability but do not remove custody risk without user claim, timeout, or queue semantics.

## Verification

- Each source repository was inspected by a dry-run subagent using `skills/harvest-patterns/SKILL.md`.
- Accepted findings were compared against the current catalog and anti-pattern list before writing updates.
- Optional or target-specific findings were rejected unless they generalized across future DeFi designs.
- Full catalog index regeneration and staged markdown validation were run before commit.
