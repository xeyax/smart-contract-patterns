# Batch 19 Findings

## Source Repositories

| Protocol | Repository | Commit | Focus |
|----------|------------|--------|-------|
| Aera V3 | `aera-finance/aera-contracts-public` | `9888a9e0d50fa38d4e86a69a8ebb9b605b08dafd` | Merkle-scoped guardian operations, frame callbacks, oracle registry, async settlement, fee snapshots |
| SunSwap V3 | `sun-protocol/sunswap-v3-contracts` | `a8551b9f95f9e888104874416fdf1b55847eba98` | TRON Uniswap V3-style AMM and periphery callback mechanics |
| OpenEden TBILL Solana | `OpenEdenHQ/openeden.tbill.solana` | `948bb2bb1c224c51ef7aeec7fc1d2bee3dcc24d4` | Token-2022 transfer hook policy gate |
| Lido Core | `lidofinance/core` | `eb4ff801ddbaa728397bc249ba6884500024d490` | Beacon deposit security and staking report sanity |
| EigenLayer | `Layr-Labs/eigenlayer-contracts` | `f84a5151080cdf0b77b9b6e46506cde723d06c28` | Multi-factor restaking slashing accounting |
| Symbiotic Core | `symbioticfi/core` | `7cb06639c5cd656d1d212dafa2c270b5fde39306` | Capture-time slashing and veto resolver windows |
| Pendle V2 | `pendle-finance/pendle-core-v2-public` | `fdcfe39ed7b45717f0e6e286581bdcf96bb2f9ce` | Fixed-maturity PT/YT, implied-rate AMM, TWAP and rewards |
| Morpho Blue | `morpho-org/morpho-blue` | `1478e9cfe1b4d514f80682b3b60e4e12ff3ee45a` | Callback-funded lending settlement and formalized accounting evidence |

## Accepted Catalog Updates

- Added [Frame-Scoped Callback Capability](../../patterns/access-control/pattern-frame-scoped-callback-capability.md), [Callback-Funded Lending Settlement](../../patterns/lending/pattern-callback-funded-lending-settlement.md), [Fixed-Yield Implied-Rate AMM](../../patterns/liquidity/pattern-fixed-yield-implied-rate-amm.md), [User Opt-In Pending Oracle Registry](../../patterns/oracles/pattern-user-opt-in-pending-oracle-registry.md), [Expiry-Bounded Gauge Emission Schedule](../../patterns/rewards/pattern-expiry-bounded-gauge-emission-schedule.md), [Fixed-Maturity Principal/Yield Tokenization](../../patterns/tokens/pattern-fixed-maturity-principal-yield-tokenization.md), [Token-2022 Transfer Hook Policy Gate](../../patterns/tokens/pattern-token2022-transfer-hook-policy-gate.md), and [Restaking Slashing Accounting Requirements](../../patterns/vaults/req-restaking-slashing-accounting.md).
- Updated selector-scoped authority, validator-operator registry, async settlement, rate-bounded NAV reporting, liquid-staking loss accounting, high-water-mark fees, TWAP, exchange-rate valuation, conservative LP collateral pricing, oracle staleness, bridged-rate relay, lazy reward indexes, reward-token accrual risk, callback settlement, isolated permissionless markets, share-denominated lending, bad-debt realization, lending freshness, credit-loss accounting, oracle reliability, public slot readers, and anti-pattern guidance.

## Rejected Or Deferred Candidates

- SunSwap concentrated liquidity, callback settlement, revert-encoded quotes, and permit-if-necessary helpers were treated as duplicate evidence for existing Uniswap V3/V2-style docs.
- Pendle cumulative Merkle claims were not added to delayed cumulative claims because the inspected source lacks an activation delay, challenge window, or cancel path.
- Pendle cross-chain exchange-rate updates were treated as oracle staleness risk, not as a positive permissionless bridged-rate relay pattern.
- OpenEden's default-frozen launch gate was not added as a standalone pattern because the reusable finding is the Token-2022 hook policy gate.
- Aera v1 Balancer-based vault evidence was used cautiously because the repository labels older dependencies as in-development/unaudited.

## Contradictions And Caveats

- SunSwap README mentions dynamic fee tiers, but inspected code is Uniswap V3-style enabled fee tiers and protocol fee bounds, not hook-governed dynamic LP fees.
- OpenEden README says `ADMIN_PUBKEY` should be a Squads multisig, but the program enforces only equality to a hardcoded public key.
- Aera's pending-oracle opt-in intentionally creates per-user or per-vault oracle divergence during the update window; it is not one canonical source during migration.
- Pendle's Chainlink-compatible oracle wrapper can report current block timestamps while the underlying implied-rate TWAP still needs readiness checks.
- EigenLayer and Symbiotic show that restaking slash accounting is not one formula: slash factors, capture windows, resolver vetoes, and rounding order must be documented.
