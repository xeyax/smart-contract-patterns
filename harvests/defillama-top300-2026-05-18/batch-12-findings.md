# Batch 12 Findings

Expanded discovery analyzed 20 additional public source repositories across Solana LSTs, RWA redemption, BTC staking, bridge, stablecoin, DEX, lending, and perps systems.

## Source Repositories

| Protocol | Repository | Commit | Focus |
|----------|------------|--------|-------|
| Spark Liquidity Layer | `sparkdotfi/spark-alm-controller` | `0fee4b5` | Route-scoped rate limits and allocator controls |
| Kelp | `Kelp-DAO/LRT-rsETH` | `3dded88` | LRT operator registry, oracle bounds, queue controls |
| Obol | `ObolNetwork/obol-splits` | `0695656` | Principal/reward withdrawal waterfalls |
| Liquid Collective | `liquid-collective/liquid-collective-protocol` | `ae4f2ce` | Validator allocation, report guardrails |
| Superstate USTB | `superstateinc/ustb` | `78e8ca2` | RWA allowlists, split pause, NAV checkpoints |
| Superstate Redemptions | `superstateinc/onchain-redemptions` | `59534af` | RWA redemption buffers and receiver semantics |
| Lista DAO | `lista-dao/lista-dao-contracts` | `3e120da` | CDP auctions, PSM reserves, liquid-staking exits |
| Lista Token | `lista-dao/lista-token` | `ce9ec49` | OFT outflow limiters |
| Babylon | `babylonlabs-io/babylon` | `d96cd9d` | BTC staking covenant and finality semantics |
| Babylon BSN | `babylonlabs-io/cosmos-bsn-contracts` | `5b93a16` | CosmWasm BTC light-client and IBC overlap |
| SolvBTC | `solv-finance/SolvBTC` | `c371d21` | ERC-3525 slot reserve wrappers |
| QuickSwap | `QuickSwap/quickswap-core` | `27a8426` | V2 AMM overlap review |
| HyperLend | `hyperlendx/hyperlend-core` | `0c2b14f` | Aave-fork overlap review |
| StarkGate | `starknet-io/starkgate-contracts` | `07e11c3` | Bridge cancellation and historical withdrawal bridges |
| GMX Synthetics | `gmx-io/gmx-synthetics` | `028c79a` | Perps PnL, reserve, funding, and ADL controls |
| Jito StakeNet | `jito-foundation/stakenet` | `0a70837` | Cranked validator maintenance and directed stake |
| SPL Stake Pool | `solana-program/stake-pool` | `439df50` | Epoch freshness and stake-pool accounting |
| Marinade | `marinade-finance/liquid-staking-program` | `2614737` | Delayed unstake tickets |
| Sanctum | `igneous-labs/S` | `66de438` | Upgrade-slot-pinned calculators and LST router value preservation |
| Jupiter Lend | `jup-ag/jupiter-lend` | `9ab5d04` | Docs/IDL reference only; no primary implementation updates |

## Accepted Catalog Updates

- Added patterns for mutually-exclusive RWA allowlists, principal/reward waterfalls, reserve-split LST receipts, covenant-gated BTC staking outputs, SFT slot wrappers, perps capped-PnL accounting, upgrade-slot-pinned Solana adapters, conservative LST router value preservation, and cranked validator maintenance.
- Added requirements for perps ADL/reserve/funding controls and Solana stake-pool epoch accounting freshness.
- Updated rate-limit, validator registry, NAV report, async exit, liquid-staking loss, operator routing, Solana account validation, BTC SPV, bridge refund, token bridge registration, bridge cutover, withdrawal buffer, liquidation auction, shared liquidity, exchange-rate valuation, and anti-pattern docs.

## Rejected Or Merged Candidates

- QuickSwap V2 AMM mechanics were merged into existing Uniswap V2-style AMM docs.
- HyperLend Aave V3 fork mechanics were rejected as covered by existing Aave-style lending and L2 sequencer sentinel guidance.
- Babylon BSN ordered IBC routing was treated as overlap with existing canonical bridge and SPV boundary docs.
- Jupiter Lend was not accepted as primary evidence because the checkout contains docs, IDLs, and reference snippets rather than implementation/tests.
- Kelp queued withdrawal and daily mint limits were merged into existing withdrawal-buffer and limiter guidance.
- Superstate and Lista admin pause, blacklist, and emergency-withdraw powers were treated as anti-pattern overlap rather than positive pattern evidence.

## Contradiction Review

- Solana current-epoch freshness is documented with liveness caveats because keeper/crank failure can stall value-changing flows.
- Sanctum value preservation is framed as accounting protection under configured calculators, not market-price safety.
- Upgrade-slot pinning is documented as a governance/liveness dependency, not a full upgrade-risk elimination.
- Babylon BTC staking is not presented as bridge custody or trustless withdrawal; covenant and finality-provider keys remain explicit assumptions.
- StarkGate cancellation is documented as delayed reclaim that can race with remote consumption and may not refund messaging fees.
- GMX perps caps and ADL are framed as exposure controls, not insolvency elimination.
- Marinade delayed unstake is not presented as pause-safe because claim requires the protocol to be unpaused.

## Verification

- Dry-run harvest subagents compared candidates against the catalog and anti-patterns before edits.
- Catalog index regeneration and staged markdown validation were run before commit.
