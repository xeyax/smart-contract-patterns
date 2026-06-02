# Batch 20 Findings

## Source Repositories

| Protocol | Repository | Commit | Focus |
|----------|------------|--------|-------|
| Kinetiq kHYPE | `code-423n4/2025-04-kinetiq` | `a3913ca2b9d021df45a428e0185ee4f4f45509ae` | L1 operation queues, directed rounding, validator performance sanity |
| RAAC | `ryzen-xp/2025-02-raac` | `3cff198ef1654e2da0ac0a2dfd2c25c5a3e13ab0` | RWA lending liquidation windows, liquidity buffer, oracle request context |
| Yield Basis | `Peter-Brad/2025-08-yield-basis-Peter-Brad-public` | `6948a65d35b95bac81198b489d8437791a24af9b` | Constant-leverage AMM, flash-liquidity virtual swaps, LP loss repricing |
| Astherus Earn | `astherus-contract/astherus-earn-contract` | `1472bad4d7267a2c9dbf490b646201ad673e9285` | Signed exchange-rate uploads, operator-funded withdrawals, destination transfer limits |
| DoubleZero Solana | `doublezerofoundation/doublezero-solana` | `4368da2c446b799f354aecb6156fc0e77343634b` | Snapshot reward distribution, debt write-offs, Solana bitmap account data |
| Euler V2 | `euler-xyz/euler-vault-kit`, `euler-xyz/ethereum-vault-connector` | `5b98b42048ba11ae82fb62dfec06d1010c8e41e6`, `b9d557a8ebcd3db1fbeef4aa60282aa4059a7bbf` | Deferred status frames, donation-smoothed savings, synth supply exclusions |
| M0 | `m0-foundation/protocol` | `b42fe5bc13b14202c684f78aaa15be284664834d` | Validator-signed collateral updates, delayed mint vetoes, dual-index liabilities |
| Kelp | `Kelp-DAO/LRT-rsETH` | `3dded885f6f797f5959aff449c3a30c5cbb6ce23` | Restaking exchange-rate relay and operator registry caveats |
| Liquid Collective | `liquid-collective/liquid-collective-protocol` | `ae4f2ce33e333fe303db5bc3503bd0730eeb959b` | Redemption interval matching and audited-key operator limits |
| Superstate USTB | `superstateinc/ustb`, `superstateinc/onchain-redemptions` | `78e8ca22a319efd265e7d6ba2c326475cb6b6e2e`, `59534af26d209ff5d3da5fda311c3a98471c1e71` | RWA allowlists, accounting pauses, effective-dated NAV checkpoints |

## Accepted Catalog Updates

- Added [Constant-Leverage Solvency AMM](../../patterns/liquidity/pattern-constant-leverage-solvency-amm.md), [Operator-Finalized Withdrawal Claim](../../patterns/vaults/pattern-operator-finalized-withdrawal-claim.md), [Height-Interval Redemption Queue](../../patterns/vaults/pattern-height-interval-redemption-queue.md), [Snapshot-Gated Integration Reward Distribution](../../patterns/rewards/pattern-snapshot-gated-integration-reward-distribution.md), and [Circulating Supply Exclusion Ledger](../../patterns/tokens/pattern-circulating-supply-exclusion-ledger.md).
- Updated async withdrawal settlement, withdrawal liquidity buffers, rate-bounded NAV reports, locked-profit smoothing, deferred status frames, lending freshness, bad-debt realization, flash-loan settlement, liquidation grace windows, balance-sheet solvency, destination-scoped rate limiting, delayed mint controls, entity/protocol allowlists, directed rounding, indexed Merkle bitmaps, historical oracle bounds, oracle staleness risk, bridged source-rate relays, and anti-pattern guidance.

## Rejected Or Deferred Candidates

- `Astherus/astherus-contract` was not counted as a source inspection because the cloned repository did not contain useful contract material for this harvest.
- `heyrapto/usual-money` was deferred because the inspected repository is front-end heavy and did not add reusable smart-contract patterns.
- `yield-basis/yb-simulations` was not used for catalog updates because the implementation audit snapshot had higher-confidence contract evidence.
- Yield Basis LP token loss-waterfall accounting was treated as related evidence for leveraged AMM and bad-debt/loss accounting; it may deserve a future dedicated vault or LP supply-repricing doc after a broader comparison pass.
- Kelp unlock queue details were used only as relay/operator-registry caveats because the inspected evidence was weaker than the existing liquid-staking queue patterns.

## Contradictions And Caveats

- Operator-funded withdrawal queues improve traceability but do not contradict permissioned-exit custody guidance; if the operator can delay or skip requests without timeout, the liveness risk remains.
- Chainlink-compatible RWA or NAV wrappers can satisfy an interface while hiding economic freshness; docs now distinguish call-time freshness from source checkpoint freshness.
- M0-style delayed mint proposals are stronger than a block-scoped throttle, so the existing throttle doc was updated as a variant instead of replacing the simpler pattern.
- RAAC's async Chainlink Functions oracle shape exposed a generalized anti-pattern: request context must be keyed by request id, not stored in one global pending subject.
