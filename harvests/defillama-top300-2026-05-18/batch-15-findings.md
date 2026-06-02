# Batch 15 Findings

Batch 15 continues the expanded DefiLlama top-300 harvest after the initial scored source map was exhausted. It includes newly cloned sources plus deeper passes over previously deferred sources from batch 14.

## Sources Inspected

| Protocol | Repository | HEAD | Notes |
|----------|------------|------|-------|
| BENQI | `benqi-fi/BENQI-Smart-Contracts` | `e0cfd244726719dfe027c9740878d64d1cad98f2` | Newly counted; batch 14 clone was deferred after a failed agent run. |
| Drift Protocol | `drift-labs/protocol-v2` | `0ae3e3b1db782a6765c3525b3dec38ad4d9d3a62` | Deeper perps pass after batch 14 deferral. |
| fx Protocol | `AladdinDAO/fx-protocol-contracts` | `5e198e93657db008a57129e7eea21a996618f17f` | Deeper dual-token stablecoin pass after batch 14 deferral. |
| QuickSwap Periphery | `QuickSwap/quickswap-periphery` | `522a94168b0814d0776d834119df377f03898807` | Deeper router/periphery pass after batch 14 deferral. |
| Aave V2 | `aave/protocol-v2` | `ce53c4a8c8620125063168620eba0a8a92854eb8` | Expanded source discovery. |
| Derive V2 | `derivexyz/v2-core` | `96796a61dcb1dc852e25518b00cc1a79fb3caeeb` | Expanded source discovery. |
| Polygon zkEVM Bridge | `0xPolygonHermez/zkevm-contracts` | `110bda5a03e70ee7331bc06407a8e79226d3e520` | Expanded source discovery. |

## Accepted Catalog Updates

### BENQI

- Added [Capped Linear Voting Escrow](../../patterns/governance/pattern-capped-linear-voting-escrow.md) from veQI linear accrual, cap, burn-on-unstake, and non-transferable voting-token behavior.
- Added [Dynamic-Power Gauge Allocation](../../patterns/governance/pattern-dynamic-power-gauge-allocation.md) from basis-point gauge preferences over current veQI voting power.
- Updated [Async Deposit/Withdrawal](../../patterns/vaults/pattern-async-deposit.md) and [Liquid Staking Loss Accounting Requirements](../../patterns/vaults/req-liquid-staking-loss-accounting.md) with sAVAX cooldown exits that bind claim basis to historical rate lookup.
- Updated [Break-Glass Risk Limiter](../../patterns/access-control/pattern-break-glass-risk-limiter.md) with a proof-of-reserve-triggered pause variant.
- Updated [ANTIPATTERNS](../../ANTIPATTERNS.md) to clarify that declared risk bounds are not controls unless setters enforce them.

### Drift Protocol

- Added [Fee-Pool Capped Asymmetric Funding](../../patterns/perps/pattern-fee-pool-capped-asymmetric-funding.md).
- Added [Position-Size Scaled Margin Requirement](../../patterns/perps/pattern-position-size-scaled-margin-requirement.md).
- Added [Progressive Liquidation State Machine](../../patterns/perps/pattern-progressive-liquidation-state-machine.md).
- Added [Instruction-Scoped Signed Message Orders](../../patterns/routing/pattern-instruction-scoped-signed-message-orders.md).
- Updated [Capped PnL Impact Pool Risk Accounting](../../patterns/perps/pattern-capped-pnl-impact-pool-risk-accounting.md), [ADL Reserve And Funding Risk Controls](../../patterns/perps/req-adl-reserve-and-funding-risk-controls.md), [Action-Scoped Bounded Risk Prices](../../patterns/oracles/pattern-action-scoped-bounded-lending-prices.md), and [Oracle Reliability Requirements](../../patterns/oracles/req-oracle-reliability.md).

### fx Protocol

- Added [Dual-Asset Stability Buffer](../../patterns/lending/pattern-dual-asset-stability-buffer.md).
- Added [Risk-Bucketed Position Ticks](../../patterns/lending/pattern-risk-bucketed-position-ticks.md).
- Updated [Action-Scoped Bounded Risk Prices](../../patterns/oracles/pattern-action-scoped-bounded-lending-prices.md), [Circuit Breaker](../../patterns/vaults/pattern-circuit-breaker.md), and [Registry-Gated Exchange Fallback](../../patterns/routing/pattern-registry-gated-exchange-fallback.md).
- Rejected fxBASE redemption cooldown as async-exit protection because claim output is live-priced at claim time.

### QuickSwap Periphery

- Added [User-Directed Liquidity Migrator](../../patterns/liquidity/pattern-user-directed-liquidity-migrator.md).
- Updated [Verified Callback Settlement](../../patterns/liquidity/pattern-verified-callback-settlement.md), [Balance Delta Transfer Accounting](../../patterns/token-integration/pattern-balance-delta-transfer-accounting.md), [TWAP Oracle](../../patterns/oracles/pattern-twap-oracle.md), and [ANTIPATTERNS](../../ANTIPATTERNS.md).
- Rejected QuickConverter and example zero-min-out flows as positive patterns; they remain anti-pattern evidence.

### Aave V2

- Added [Packed Reserve Risk Configuration](../../patterns/lending/pattern-packed-reserve-risk-configuration.md).
- Added [Nontransferable Debt Token Delegation](../../patterns/lending/pattern-nontransferable-debt-token-delegation.md).
- Updated [Scaled Balance Token Accounting](../../patterns/lending/pattern-scaled-balance-token-accounting.md), [Lending Accounting Freshness Requirements](../../patterns/lending/req-lending-accounting-freshness.md), [Debt-Converting Flash Loan](../../patterns/lending/pattern-debt-converting-flash-loan.md), [Collateral Threshold Separation Requirements](../../patterns/lending/req-collateral-threshold-separation.md), and [Oracle Staleness Risk](../../patterns/oracles/risk-oracle-staleness.md).
- Rejected Aave V2 as evidence for V3-only supply caps, isolation mode, eMode, and modern Chainlink freshness practice.

### Derive V2

- Added [Hook-Validated Subaccount Ledger](../../patterns/access-control/pattern-hook-validated-subaccount-ledger.md).
- Added [Scenario-Shocked Portfolio Margin](../../patterns/perps/pattern-scenario-shocked-portfolio-margin.md).
- Added [Manager-Owned Derivative Cash Settlement](../../patterns/perps/pattern-manager-owned-derivative-cash-settlement.md).
- Added [Solvency-Tiered Portfolio Liquidation Auction](../../patterns/perps/pattern-solvency-tiered-portfolio-liquidation-auction.md).
- Updated [ADL Reserve And Funding Risk Controls](../../patterns/perps/req-adl-reserve-and-funding-risk-controls.md) and [Threshold Reporter Consensus](../../patterns/oracles/pattern-threshold-reporter-consensus.md).

### Polygon zkEVM / Agglayer Bridge

- Added [Sovereign Bridge Local Balance Tree](../../patterns/cross-chain/pattern-sovereign-bridge-local-balance-tree.md).
- Updated [Domain-Scoped Message Root Accumulator](../../patterns/cross-chain/pattern-domain-scoped-message-root-accumulator.md), [Proof Bridge Exit Safety Requirements](../../patterns/cross-chain/req-proof-bridge-exit-safety.md), [Deterministic Cross-Chain Factory](../../patterns/cross-chain/pattern-deterministic-cross-chain-factory.md), [Bridge-Owned Mintable Token Pair](../../patterns/cross-chain/pattern-bridge-owned-mintable-token-pair.md), [Retryable Cross-Domain Message Ledger](../../patterns/cross-chain/pattern-retryable-cross-domain-message-ledger.md), and [Bridge Exit Liveness Requirements](../../patterns/cross-chain/req-bridge-exit-liveness.md).
- Recorded broad emergency bridge pauses as a break-glass exception that can trap claims and exits if not scoped operationally.

## Rejected Or Deferred

- Aera V3 source discovery found references but the attempted GitHub clone was inaccessible; it is not counted as inspected.
- Mantle Bridge, Avalanche Core Bridge, USDT0, Tectonic, Usual, and other top-300 sources remain discovery targets.
- Drift ADL was not accepted as direct ADL evidence; accepted Drift material covers funding, liquidation, PnL settlement, bankruptcy, and socialized-loss mechanics.
- Derive EIP-1271 account-abstraction permit evidence was not accepted because the inspected tests were EOA-focused.

## Contradictions Resolved

- The action-scoped oracle pattern was generalized from lending-only wording to risk-price wording so perps evidence does not get forced into lending terminology.
- Aave V2 liquidation configuration was used only for non-inversion and liquidation-bonus calibration, not to weaken the catalog's stricter threshold-separation recommendation.
- Polygon zkEVM/Agglayer wrapped-token evidence was captured as a bridge-registry identity variant, not as a contradiction of token-stored remote identity.
- Agglayer low-level receiver success was separated from semantic application acknowledgement in the retryable message guidance.
