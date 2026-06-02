# Batch 26 Findings

## Source Repositories

| Protocol | Repository | Commit | Focus |
|----------|------------|--------|-------|
| Aave GHO | `aave/gho-core` | `c6335a0bb9cba099960c5378b1ff0db190b8da8f` | Stablecoin facilitators, GSM, stewards |
| Aave V3 Core | `aave/aave-v3-core` | `782f51917056a53a2c228701058a6c3fb233684a` | Reserve risk, eMode, siloed borrowing |
| Aave V3 Periphery | `aave/aave-v3-periphery` | `8bb2493678bbb31532249f1e488fffe5f53a2d1a` | Rewards controller and transfer strategies |
| Uniswap Permit2 | `Uniswap/permit2` | `cc56ad0f3439c502c246fc5cfcc3db92bb8b7219` | Scoped permits and nonce bitmaps |
| Uniswap Universal Router | `Uniswap/universal-router` | `5a5336a2aa69faea5407ad610feabed6d5a1c4fa` | Command router and partial-failure cleanup |
| Uniswap Swap Router Contracts | `Uniswap/swap-router-contracts` | `70bc2e40dfca294c1cea9bf67a4036732ee54303` | TWAP slippage and revert quotes |
| Uniswap V3 Staker | `Uniswap/v3-staker` | `6d06fe4034e4eec53e1e587fc4770286466f4b35` | Range-liquidity incentives |
| Curve StableSwap NG | `curvefi/stableswap-ng` | `2abe778f40206a6c0fd108a0a53ad3266cbedeee` | Stable invariant, fees, stored balances |
| Curve Crypto | `curvefi/curve-crypto-contract` | `d7d04cd9ae038970e40be850df99de8c1ff7241b` | Crypto invariant and callback settlement |
| Curve DAO | `curvefi/curve-dao-contracts` | `fa127b1cb7bf83e4f3d605f7244b7b4ed5ebe053` | Voting escrow, gauges, fee distribution |
| MetaMorpho | `morpho-org/metamorpho` | `163eb2ae022629d4c35e598a668a30451af25f44` | Curated lending vaults |
| Morpho Blue Oracles | `morpho-org/morpho-blue-oracles` | `e32d8902f9518365caa53e9eaed3cbd6cb017a63` | Chainlink-compatible oracle wrappers |
| Morpho Blue IRM | `morpho-org/morpho-blue-irm` | `a1a87fd5a7ee13873ea9d2bbd87e9c7b2cdbbef3` | Adaptive and fixed-rate IRMs |
| 1inch Spot Price Aggregator | `1inch/spot-price-aggregator` | `8911f1582347172876b72ea4225106232f4aaab2` | Off-chain spot aggregation boundary |

`1inch/aggregation-router-v6` was unavailable during this batch and is not
counted.

## Accepted Catalog Updates

- Added [Adaptive Price-Scale Crypto Invariant](../../patterns/liquidity/pattern-adaptive-price-scale-crypto-invariant.md) and [Time-Decaying Lock Voting Escrow](../../patterns/governance/pattern-time-decaying-lock-voting-escrow.md).
- Updated Aave/GHO guidance for facilitator issuance buckets, cooldown-bounded stewards, hysteretic swap freezers, eMode debt cohorts, siloed borrowing, reserve freeze vs pause, and reward transfer strategies.
- Updated Uniswap guidance for Permit2-scoped approvals, unordered nonce bitmaps, command-router partial failure cleanup, per-hop route slippage, synthetic TWAP execution guards, revert-encoded quotes, and range-liquidity reward lifecycle bounds.
- Updated Curve guidance for stable invariant solving, invariant-delta LP accounting, virtual-price monotonicity, off-peg and concentration fees, AMM EMA oracle scope, callback settlement, delayed parameter commits, voting escrow, gauge allocation, fee-distribution buckets, and bounded token inflation.
- Updated Morpho and 1inch guidance for monotonic risk-reduction controls, bounded market queues, virtual-share offset strength, ERC4626 share-price oracle risk, Chainlink-compatible freshness assumptions, adaptive IRMs, bounded exponential math, one-shot fixed-rate initialization, and off-chain-only spot aggregation.

## Rejected Or Deferred Candidates

- Standalone Permit2, curated lending vault, Morpho Chainlink multihop oracle, Curve FeeDistributor, and ERC4626/rate-oracle pool pages were rejected as better handled by existing docs.
- Aave packed reserve config, scaled debt accounting, debt-converting flash loans, L2 sequencer sentinel, isolation-mode debt ceilings, and ParaSwap registry/slippage checks were already covered.
- Curve canonical factory evidence was rejected because NG factories are registry/deployer infrastructure rather than one canonical pool per token pair.
- 1inch spot aggregation was rejected as on-chain multi-source validation because the repository explicitly marks it off-chain only.
- Curve `VotingEscrow.assert_not_contract` remains an EOA-gate caveat for governance anti-tokenization policy, not a general security pattern.

## Contradictions And Caveats

- Cooldown-bounded immediate steward updates are not timelocks; the catalog now distinguishes queued timelocks from post-action rate limits.
- Aave eMode supports a bounded category of debt assets, so elevation-mode wording was broadened from "one debt asset" to bounded debt cohorts.
- Chainlink-compatible oracle interfaces do not imply Chainlink heartbeat, min/max answer, or freshness semantics.
- Virtual share offsets reduce first-depositor inflation risk, but offset strength can still be weak for high-decimal assets.
- Curve Crypto has delayed commits, while StableSwap NG has bounded immediate fee setters; "Curve templates timelock fee/admin changes" is too broad.
- CryptoPoolProxy-style `emergency_admin` kill and unkill powers are not monotonic break-glass evidence.
