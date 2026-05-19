# Batch 18 Findings

Batch 18 continues the expanded DefiLlama top-300 harvest after batch 17. It covers stablecoin/RWA issuance flows, Stacks lending contracts, Reserve Protocol core, Frax/Fraxlend source, and Lorenzo BTC bridge/staking sources.

## Sources Inspected

| Protocol | Repository | HEAD | Notes |
|----------|------------|------|-------|
| Avant Protocol avUSD | `Avant-Protocol/avUSD-Contracts` | `43858abc5a3c481e3b2d02790d168b88e630e7b1` | Signed mint/redeem, custody routing, block throttles, staking vault reward vesting. |
| Avant Protocol Core | `Avant-Protocol/Avant-Core-Contracts` | `13dafc691881ae19300edca6d02d64291b24a2fb` | AvantCoin variant of the same mint/redeem and staking mechanics; used as duplicate evidence only. |
| Avant MAX | `Avant-Protocol/Avant-Contracts-Max` | `ee40a93ea19831e86b2c8581541206f461488828` | Async MAX request manager and bounded price storage. |
| Zest Protocol | `Zest-Protocol/zest-contracts` | `3564bc38906e464ec4de774122bb9bbaee20ddc6` | Clarity lending pool, e-mode, isolation mode, reserve caps, zTokens, incentives, Pyth adapters. |
| Reserve Protocol Core | `reserve-protocol/protocol` | `9cda9d89c871e70886fc4453f94fc6aa889445df` | RToken, basket handler, recollateralization, staking, broker, version registry, collateral plugins. |
| Frax Solidity | `FraxFinance/frax-solidity` | `30532c8cefcbf5c7efafcff4369261bd435a4859` | Fraxswap TWAMM, Fraxferry v1/v2, FPI, FXB, oracle sources. |
| Fraxlend | `FraxFinance/fraxlend` | `2bed49d4dcc6702d92dede825c3424893517d841` | Pair-level lending, share accounting, low/high oracle prices, adaptive rate code. |
| Lorenzo Chain | `Lorenzo-Protocol/lorenzo` | `ee65c41e485ad7b57f4e40d0230c029354610a7d` | Cosmos/Ethermint BTC light client, BTC staking, BNB proof module, stake plans. |
| Lorenzo enzoBTC | `Lorenzo-Protocol/enzoBTC_contract` | `5951bff2cd51a3ac91a239ed6ca73aca095986dd` | Guardian mint security, custody, strategy manager, withdrawals, token admin paths. |
| Lorenzo Audit Reports | `Lorenzo-Protocol/audit-report` | `ad19cbec84f953a12213576dff50e72fa41b0988` | Audit PDFs used only as corroboration where target source code existed. |

## Accepted Catalog Updates

### Avant Protocol

- Added [Block-Scoped Mint/Redeem Throttle](../../patterns/access-control/pattern-block-scoped-mint-redeem-throttle.md) from avUSD per-block mint and redeem limits.
- Added [Two-Step Delegated Order Signer](../../patterns/access-control/pattern-two-step-delegated-order-signer.md) from avUSD pending/accepted delegated signer flow.
- Added [Oracle-Computed Async Settlement](../../patterns/vaults/pattern-oracle-computed-async-settlement.md) from MAX V2 request completion that computes economics from request data and price storage.
- Updated [Historical Bounds](../../patterns/oracles/pattern-historical-bounds.md), [Break-Glass Risk Limiter](../../patterns/access-control/pattern-break-glass-risk-limiter.md), [Locked Profit Smoothing](../../patterns/vaults/pattern-locked-profit-smoothing.md), and [ANTIPATTERNS](../../ANTIPATTERNS.md) with bounded price storage, gatekeeper, reward vesting, token onboarding, and decimal-sentinel evidence.

### Zest Protocol

- Added [Clarity Trait Cohort Validation](../../patterns/access-control/pattern-clarity-trait-cohort-validation.md) from trait-typed asset/oracle/zToken cohort checks.
- Added [Liquidation Grace Period With Bad-Debt Escape](../../patterns/lending/pattern-liquidation-grace-period-with-bad-debt-escape.md) from asset grace-period liquidation rules.
- Updated [Elevation-Scoped Borrow Mode](../../patterns/lending/pattern-elevation-scoped-borrow-mode.md), [Reserve Exposure Caps](../../patterns/lending/pattern-reserve-exposure-caps.md), [Scaled Balance Token Accounting](../../patterns/lending/pattern-scaled-balance-token-accounting.md), [Lazy Borrow Index](../../patterns/lending/pattern-lazy-borrow-index.md), [Lazy Reward Index](../../patterns/rewards/pattern-lazy-reward-index.md), [Oracle Reliability Requirements](../../patterns/oracles/req-oracle-reliability.md), and [ANTIPATTERNS](../../ANTIPATTERNS.md).

### Reserve Protocol Core

- Added [Paired Supply-Change Throttle](../../patterns/tokens/pattern-paired-supply-change-throttle.md) from RToken issuance/redemption throttles.
- Added [Target-Unit Backup Basket Substitution](../../patterns/tokens/pattern-target-unit-backup-basket-substitution.md) from basket target-name backup selection.
- Added [Historical Basket Redemption Nonces](../../patterns/tokens/pattern-historical-basket-redemption-nonces.md) from custom redemption against stored basket history.
- Added [Tripwire Dutch Auction Fallback](../../patterns/routing/pattern-tripwire-dutch-auction-fallback.md) from broker-managed Dutch auction disablement.
- Added [Shared Component Reentrancy Lock](../../patterns/access-control/pattern-shared-component-reentrancy-lock.md) from protocol-wide component reentrancy state.
- Added [Cumulative Draft Unstaking Queue](../../patterns/rewards/pattern-cumulative-draft-unstaking-queue.md) from stRSR delayed unstaking drafts and era resets.
- Updated [Oracle Staleness Risk](../../patterns/oracles/risk-oracle-staleness.md) and [Version-Gated Upgrade Registry](../../patterns/upgrades/pattern-version-gated-upgrade-registry.md) with stale-price degradation and Reserve core version-registry evidence.

### Frax

- Added [Lazy Virtual-Order TWAMM](../../patterns/liquidity/pattern-lazy-virtual-order-twamm.md) from Fraxswap long-term order pools and lazy virtual execution.
- Added [Dispute-Windowed Operator Batch Bridge](../../patterns/cross-chain/pattern-dispute-windowed-operator-batch-bridge.md) from Fraxferry v1 optimistic batch bridge.
- Added [Liquidity-Captain Storage-Proof Bridge](../../patterns/cross-chain/pattern-liquidity-captain-storage-proof-bridge.md) from Fraxferry V2 captain liquidity and storage-proof reimbursement.
- Updated [Action-Scoped Bounded Risk Prices](../../patterns/oracles/pattern-action-scoped-bounded-lending-prices.md), [Share-Denominated Lending Accounting](../../patterns/lending/pattern-share-denominated-lending-accounting.md), [Explicit Bad-Debt Realization](../../patterns/lending/pattern-explicit-bad-debt-realization.md), and [ANTIPATTERNS](../../ANTIPATTERNS.md) with Fraxlend and Fraxferry caveats.

### Lorenzo Protocol

- Added [Value-Tiered Source Finality](../../patterns/cross-chain/pattern-value-tiered-source-finality.md) from amount-tiered Bitcoin confirmation requirements.
- Updated [Bitcoin SPV State Transition Gate](../../patterns/cross-chain/pattern-bitcoin-spv-state-transition-gate.md), [Chain-Bound Request Hash](../../patterns/cross-chain/pattern-chain-bound-request-hash.md), [Custodian-Attested Mint/Burn](../../patterns/cross-chain/pattern-custodian-attested-mint-burn.md), and [ANTIPATTERNS](../../ANTIPATTERNS.md) with BTC light-client, guardian-mint, withdrawal-custody, BNB proof-boundary, beacon, and privileged-mint evidence.

## Rejected Or Deferred

- Avant signed custody-routed mint/redeem was treated as additional evidence for the existing custody-routed mint pattern, not a new pattern.
- Avant MAX fee-on-transfer and decimal assumptions were captured as anti-pattern updates rather than standalone docs.
- Zest kinked utilization, continuous-compounding Taylor math, governance emergency teams, and BTC HTLC scripts were rejected as duplicate, under-tested, or source-incomplete.
- Reserve pause/freeze matrix, asset-plugin isolation, monitoring facades, and P0/P1 differential testing were rejected as duplicate or outside the current catalog scope.
- Fraxlend adaptive utilization drift was deferred because the inspected snapshot lacked substantive tests; Fraxlend share accounting and bad-debt evidence was added only to existing docs.
- Lorenzo audit-report-only claims were rejected unless target source corroborated them.

## Contradictions Resolved

- Avant MAX README describes pending burn fees as retroactively changeable, but MAX V2 code snapshots burn fee at request time; the catalog uses source and tests over prose.
- Zest `Clarinet_earn.toml` references missing `contracts/v2_sbtc` paths, so BTC HTLC material was not treated as implemented source evidence.
- Reserve documentation describes a different Dutch auction phase split than the implementation; the tripwire pattern relies on code and tests.
- Fraxferry v1 is described as an optimistic batch bridge, not a proof bridge; owner and pause powers remain explicit trust assumptions.
- Lorenzo BTC paths are described with relay/reporter trust boundaries, and BNB proof paths are not described as trustless validator-finality verification.
