# Batch 29 Findings

Expanded source-discovery batch covering PumpSwap transfer-hook authority, Yield Basis simulations, Aerodrome V1, Teller V2, Inverse FiRM, BendDAO, Ribbon V2, Premia, Set Protocol V2, dHEDGE, Tokemak V2, and mStable.

## Repositories

| Protocol | Repository | Commit |
|----------|------------|--------|
| PumpSwap Transfer Hook Authority | `pump-fun/transfer-hook-authority` | `d5664eeb0dd13afe25f77b119ffd8425a23bfbaf` |
| Yield Basis Simulations | `yield-basis/yb-simulations` | `e22d13db7b4d5c74266b46f40168829615e479b6` |
| Aerodrome V1 | `aerodrome-finance/contracts` | `1ba30815bba620f7e9faa34769ffd00c214c9b82` |
| Teller V2 | `teller-protocol/teller-protocol-v2` | `49c0be13f5371c71fa9c97af78509a16c23d3626` |
| Inverse FiRM | `InverseFinance/FiRM` | `6cd9f06cd0da79ccaad9f663aed299ef3021af10` |
| BendDAO | `BendDAO/bend-lending-protocol` | `81c90c06373bd6cc616ed0d0712fe382cad56548` |
| Ribbon V2 | `ribbon-finance/ribbon-v2` | `9a7c788f123cf1e82b207b1ddbcddcab14727019` |
| Premia | `premiafinance/premia-contracts` | `0ed54a91c6b69b17a8cc9d6208aadb442218a07f` |
| Set Protocol V2 | `SetProtocol/set-protocol-v2` | `63d6cf5d09fb5cccf5e8032be3e384c433f7ef35` |
| dHEDGE | `dhedge/V2-Public` | `3437aa9dfee716e7a9381a902adb2ae7deecbad0` |
| Tokemak V2 | `Tokemak/v2-core-pub` | `de163d5a1edf99281d7d000783b4dc8ade03591e` |
| mStable | `mstable/mStable-contracts` | `51da0272104d207abcbecb5dd545fec2e6abbfe9` |

## Accepted New Patterns

- `patterns/liquidity/pattern-polynomial-stable-pair-invariant.md` captures Aerodrome's Solidly-style stable-pair polynomial invariant and router quote boundary.
- `patterns/governance/pattern-managed-voting-escrow-aggregator.md` captures Aerodrome's managed veNFT voting escrow aggregation and rebase/reward relay behavior.
- `patterns/lending/pattern-consumable-borrow-right-credit-meter.md` captures Teller's lender-attested, one-time borrow commitments that burn available credit as loans are accepted.
- `patterns/lending/pattern-receipt-wrapped-nft-collateral-loan.md` captures BendDAO's receipt-token custody wrapper for NFT-backed debt positions.
- `patterns/lending/pattern-repayment-liveness-fallback-escrow.md` captures BendDAO's repay-path fallback escrow for debt settlement when NFT transfer or liquidation state prevents direct repayment finalization.
- `patterns/vaults/pattern-epoch-rolled-covered-option-vault.md` captures Ribbon's epoch vault flow for locking collateral, minting options, auctioning them, and rolling to the next strike.
- `patterns/liquidity/pattern-collateralized-option-liquidity-pool.md` captures Premia's collateralized option-pool liquidity, underwriter lock accounting, and fee/reward indexing.
- `patterns/vaults/pattern-module-owned-portfolio-position-ledger.md` captures Set Protocol's controller-authorized module ownership of portfolio component position units.
- `patterns/vaults/pattern-adapter-routed-index-rebalance.md` captures Set Protocol's exchange-adapter-routed rebalance flow with quote asset and slippage boundaries.
- `patterns/vaults/pattern-action-scoped-nav-range-accounting.md` captures dHEDGE's different manager, deposit, withdrawal, and asset-enable valuation modes around one portfolio state.

## Merged Into Existing Patterns

- Aerodrome V1 constant-product pools, fee escrow, gauge allocation, minter emissions, factory constraints, and fee-on-transfer router paths were merged into existing liquidity, governance, rewards, access-control, and token-integration patterns.
- Inverse FiRM pessimistic feeds, daily-low borrower credit, feed switching, and fixed-rate debt accounting were merged into oracle reliability, bounded lending-price, pending-oracle, and scaled-balance lending guidance.
- Teller V2 fee-on-transfer rejection and commitment accounting were split between balance-delta token integration and the new consumable credit-meter pattern.
- BendDAO NFT price records, TWAP validation, borrow/auction freshness checks, and repayment edge cases were merged into bounded lending-price guidance and the new NFT collateral and repayment fallback patterns.
- Ribbon V2, Premia, Set Protocol V2, dHEDGE, Tokemak V2, and mStable evidence was merged into existing vault, rewards, NAV, proportional withdrawal, premium buffer, locked-profit, hysteretic allocator, amplified stable invariant, adaptive crypto invariant, and balance-delta transfer patterns.
- Yield Basis simulation code was used only as corroborating AMM-model evidence because the inspected repo is simulation-oriented rather than a deployed contract source.

## Anti-Pattern Updates

- `ANTIPATTERNS.md` now tightens unrestricted admin guidance for pricing, strike, premium, gauge, factory, and guard configuration.
- Pause guidance distinguishes swap-only AMM pause controls from pauses that trap deposits, withdrawals, repayments, or claims.
- EOA-gate guidance records the narrow bot-delay caveat and keeps the security-control warning intact.
- Synthetic freshness guidance now covers consumers that discard timestamps returned by Chainlink-compatible feeds.
- Unbounded iteration, quote/execution formula drift, missing slippage, hook/callback trust, privileged supply mutation, and fee-on-transfer blindness were expanded with batch-29 AMM, option, vault, portfolio, and lending evidence.

## Deferred Or Rejected Candidates

- PumpSwap transfer-hook authority was rejected for catalog updates in this batch because the inspected repository exposes no reusable Token-2022 transfer-hook implementation surface beyond an empty Anchor-style authority shell.
- Yield Basis `yb-simulations` was deferred as simulation evidence only; it did not justify a production pattern without on-chain invariant, admin, or settlement code.
- Aerodrome's volatile pair mechanics were merged into existing constant-product AMM guidance instead of creating a duplicate DEX pattern.
- Tokemak allocator and dHEDGE manager controls were merged into existing debt allocator, NAV, and guard patterns rather than becoming protocol-specific manager patterns.
