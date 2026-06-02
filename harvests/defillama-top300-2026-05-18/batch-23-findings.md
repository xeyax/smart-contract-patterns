# Batch 23 Findings

## Source Repositories

| Protocol | Repository | Commit | Focus |
|----------|------------|--------|-------|
| Strata Markets | `Strata-Markets/contracts` | `ad6e401c98503bbf46793da6ee923388cbec62c2` | Coverage-gated tranched exits, projected versus realized accounting |
| Exponent | `exponent-finance/exponent-core` | `2897c660eeef647002b62ba971e19457182e0b37` | Solana fixed-maturity principal/yield vaults |
| Ember Protocol | `ember-protocol/Ember-Vaults-EVM` | `11ce048163338d944677e22f811dbd80eaf094c6` | Liability-rate vault accounting, async withdrawal queue |
| Mainstreet | `Mainstreet-Labs/mainstreet-core` | `d53858244964d86eaeab3445e1942871b8a20c66` | Coverage-haircut cooldown exits |
| UNCX Network V2 | `uncx-network/liquidity-locker-univ2-contracts` | `bf76b16c5e2d51e7335e41e5016a47f14de37f9b` | LP-lock and migrator anti-pattern review |
| SolanaVault Liquid Unstaker | `SolanaVault/liquid-unstaker-client` | `50cd1f47493576a3a19ae829b24e3d4e1218b975` | Instant-unstake fee quoting from IDL and CLI integration |
| Cooler Loans | `OlympusDAO/olympus-v3` | `120266b021f1eaa0c46b00af0114bd47bbc9e590` | Borrow-capacity ramp, receipt liabilities, treasury borrow adapter |
| FAssets | `flare-foundation/fassets` | `37c1be508a33c0d0ce31216aef45958fd4e5281e` | Bridge custody queues, FTSO price store, collateral pool rewards |
| Meteora DLMM | `MeteoraAg/dlmm-sdk` | `cb777faff57d7315753dd0c6d1d639bac4473fd9` | DLMM quote math and multi-liquidity quote tests |

## Accepted Catalog Updates

- Added [Coverage-Ratio Gated Tranche Exits](../../patterns/vaults/pattern-coverage-ratio-gated-tranche-exits.md) and [Projected Versus Realized NAV Split](../../patterns/vaults/pattern-projected-realized-nav-split.md).
- Updated tiered loss waterfall requirements with first-loss coverage exits, async withdrawal guidance with cooldown haircuts, bounded request ledgers, and process-time repricing, and NAV reporting guidance with liability-rate vault accounting.
- Updated lending and oracle docs for Olympus-style monotonic borrower-favorable LTV ramps, namespaced receipt liability solvency, and treasury borrower adapters.
- Updated fixed-maturity principal/yield tokenization, dynamic premium, DLMM bin liquidity, threshold reporter consensus, lazy reward indexes, custodian-backed bridge docs, reserve-backing requirements, and anti-pattern guidance.
- Captured Flare FAssets custody queues, epoch oracle roots, collateral-pool fee-debt accounting, and initialized implementation/facet guards as reusable evidence.

## Rejected Or Deferred Candidates

- Strata meta-token and multi-token ERC4626 preview details were too project-specific to become standalone catalog patterns.
- Ember permit deposits, validator allowlists, and basic fee mechanics map to existing token/access guidance.
- Exponent lazy reward indexes and claim-window limits already fit existing reward and bounded-claim docs.
- Meteora Token-2022 handling and bitmap traversal were duplicates of existing Token-2022 and discrete-bin guidance.
- SolanaVault stake-pool discovery and unstake account selection were left as integration details because the inspected repository primarily contains IDL and CLI material.
- UNCX migrator, owner fee, referral, and country-code controls were used only as generalized anti-pattern signals; no implementation text was copied from files that reserve rights.
- Olympus batch liquidation, delegated collateral, convertible deposit, and auctioneer mechanics need a deeper pass before becoming catalog updates.

## Contradictions And Caveats

- Strata coverage gates are useful only if deposits, withdrawals, and accounting updates cannot cheaply manipulate the coverage ratio.
- Projected NAV must remain labeled as projected; treating expected accrual as realized cash contradicts the vault accounting guidance.
- Ember withdrawal requests are estimates until operator processing. The catalog now describes this as process-time rate risk, not fixed user entitlement.
- Olympus LTV ramps are borrower-favorable capacity increases and should not be merged with risk-reducing liquidation-threshold ramp-down patterns.
- SolanaVault is counted as lower-confidence integration evidence because the checkout exposes IDL and CLI behavior rather than the on-chain implementation.
- Meteora DLMM evidence is SDK/source-material quote parity evidence, not primary proof of on-chain program behavior.
- Flare custody queues depend on governance-limited agent and destination counts; solvency invariants do not eliminate malicious-governance or unbounded-governance-set risks.
