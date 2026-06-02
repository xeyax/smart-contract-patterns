# Batch 17 Findings

Batch 17 continues the expanded DefiLlama top-300 harvest after batch 16. It covers one multi-collateral CDP/rewards system, one stablecoin/savings/leverage system, one canonical bridge implementation, and one audit-report-only cross-chain stablecoin source.

## Sources Inspected

| Protocol | Repository | HEAD | Notes |
|----------|------------|------|-------|
| Satoshi Protocol Core | `Satoshi-Protocol/satoshi-core` | `7f5eddaed965904fde10ea1d40c4c4b3ea118ada` | Multi-collateral CDP, troves, stability pool, oracles, Nexus mint/redeem, collateral vaults. |
| Satoshi Protocol Farm | `Satoshi-Protocol/satoshi-farm` | `174d930eb3c220fa3163a677cea019fc1550074e` | Staking farms, lazy reward indexes, delayed claims, limited LayerZero evidence. |
| Reservoir Core | `reservoir-protocol/reservoir` | `95c83d4512a1042f241842431d53d44c0d204801` | Stablecoin issuance controller, PSM, savings module, term debt, invariants. |
| Reservoir sRUSD | `reservoir-protocol/srusd` | `cc34c9ecb30eaf13d567df42f6d9bd165e4c2914` | ERC4626-style savings token and migration contract. |
| Reservoir sRUSD Loop | `reservoir-protocol/srusd-loop` | `f97aaab1ff1028601e2fa888f1161978cf3711ed` | Morpho leverage helper and callback settlement flows. |
| Sophon Bridge | `sophon-org/custom-usdc-bridge` | `72b36f11fb6c901380836043a43c738c434d5c12` | Custom zkSync-style USDC bridge with shared custody and chain-scoped accounting. |
| USDT0 Audit Reports | `Everdawn-Labs/usdt0-audit-reports` | `c327f1732fcd6bf4f44f3cfb32903059baf41768` | Audit-report-only evidence for OFT, native mesh, deployment, and migration checks. |

## Accepted Catalog Updates

### Reservoir Protocol

- Added [Liability-Backed ERC4626 Savings Share](../../patterns/vaults/pattern-liability-backed-erc4626-savings-share.md) from sRUSD v2's burn-on-deposit, mint-on-withdraw ERC4626 liability token.
- Added [Balance-Sheet Solvency Gate](../../patterns/lending/pattern-balance-sheet-solvency-gate.md) from Reservoir's issuance controller, per-module debt caps, and asset/equity/liquidity ratio invariants.
- Added [Rolling Fixed-Maturity Debt Tokens](../../patterns/lending/pattern-rolling-fixed-maturity-debt-tokens.md) from Reservoir's ERC1155 term debt and coupon-ladder variant.
- Updated [Balance Delta Transfer Accounting](../../patterns/token-integration/pattern-balance-delta-transfer-accounting.md) with PSM received-amount minting and decimal-normalization caveats.
- Updated [Oracle Staleness Risk](../../patterns/oracles/risk-oracle-staleness.md) and [Exchange-Rate Valuation Risk](../../patterns/oracles/risk-exchange-rate-valuation.md) with stale-to-peg fallback and internal savings-rate collateral valuation risks.
- Updated [User-Directed Liquidity Migrator](../../patterns/liquidity/pattern-user-directed-liquidity-migrator.md) and [Shared Liquidity Kernel](../../patterns/liquidity/pattern-shared-liquidity-kernel.md) with savings-vault migration and leveraged callback helper variants.

### Sophon Bridge

- Added [Domain-Scoped Bridge Custody Ledger](../../patterns/cross-chain/pattern-domain-scoped-bridge-custody-ledger.md) from Sophon's per-chain balance ledger inside a shared USDC bridge escrow.
- Updated [Escrow Mint-Burn Refund Fallback](../../patterns/cross-chain/pattern-escrow-mint-burn-refund-fallback.md) with failed-deposit transaction-handle refund semantics.
- Updated [Canonical Bridge Counterpart Validation](../../patterns/cross-chain/pattern-canonical-bridge-counterpart-validation.md) and [Proof Bridge Exit Safety Requirements](../../patterns/cross-chain/req-proof-bridge-exit-safety.md) with chain-scoped sender proofs, selector checks, and payload-length checks.
- Updated [Selector-Scoped Authority](../../patterns/access-control/pattern-selector-scoped-authority.md) and [Two-Step Authority Handoff](../../patterns/access-control/pattern-two-step-authority-handoff.md) with one-shot bridge peer registration and pending-admin overwrite caveats.

### Satoshi Protocol

- Added [Nonce-Bound Delayed Reward Claim Ledger](../../patterns/rewards/pattern-nonce-bound-delayed-reward-claim-ledger.md) from Satoshi Farm's delayed reward claim id and status ledger.
- Updated [Hint-Assisted Risk-Ordered Position List](../../patterns/lending/pattern-hint-assisted-risk-ordered-position-list.md), [Product-Sum Stability Pool Accounting](../../patterns/lending/pattern-product-sum-stability-pool-accounting.md), and [Lazy Borrow Index](../../patterns/lending/pattern-lazy-borrow-index.md) with multi-collateral CDP variants.
- Updated [Reserve Exposure Caps](../../patterns/lending/pattern-reserve-exposure-caps.md), [Lazy Reward Index](../../patterns/rewards/pattern-lazy-reward-index.md), and [Withdrawal Liquidity Buffer](../../patterns/vaults/pattern-withdrawal-liquidity-buffer.md) with debt caps, clamped emission windows, and collateral-vault recall evidence.
- Updated [Action-Scoped Bounded Risk Prices](../../patterns/oracles/pattern-action-scoped-bounded-lending-prices.md), [Conservative AMM LP Collateral Oracle](../../patterns/oracles/pattern-conservative-amm-lp-collateral-oracle.md), [Multi-Source Validation](../../patterns/oracles/pattern-multi-source-validation.md), and [ANTIPATTERNS](../../ANTIPATTERNS.md) with oracle-bound, LP-pricing, source-averaging, and asymmetric-staleness lessons.

### USDT0 Audit Reports

- Updated [ANTIPATTERNS](../../ANTIPATTERNS.md) with divergent message parsing between authorization and execution.
- Updated [Bridge Exit Liveness Requirements](../../patterns/cross-chain/req-bridge-exit-liveness.md), [Custodial Reserve Backing Requirements](../../patterns/cross-chain/req-custodial-reserve-backing.md), and [Bridge-Owned Mintable Token Pair](../../patterns/cross-chain/pattern-bridge-owned-mintable-token-pair.md) with audit-source migration, reserve, compose retry, and refund checks.
- Updated [Bootstrap Authority Handoff](../../patterns/access-control/pattern-bootstrap-authority-handoff.md), [Consumer-Scoped Rate Limiter](../../patterns/access-control/pattern-consumer-scoped-rate-limiter.md), and [Canonical Bridge Counterpart Validation](../../patterns/cross-chain/pattern-canonical-bridge-counterpart-validation.md) with audit-source deployment authority, rate-limit refill, and OFT lane preflight checklists.

## Rejected Or Deferred

- `Satoshi-Protocol/satoshi-v2` was inaccessible or private during this pass and is not counted as inspected.
- Satoshi's LayerZero compose farm path was rejected for standalone pattern extraction because the main LayerZero test body is commented out.
- Satoshi's Merkle airdrop was rejected as weaker than the existing indexed Merkle airdrop pattern.
- Reservoir's bare role-gated ERC20 minters, PSM pause, token recovery, hardcoded constants, and ERC20 facade over ERC1155 terms were rejected as already covered or too project-specific.
- Sophon's L2 positive-path tests are commented out, so L2 behavior was used only where L1 code and tests corroborated the claim.
- USDT0 OneSig / threshold-signed Merkle operational batches were deferred until source code can corroborate the audit-report descriptions.
- USDT0 audit-only claims were merged into requirements, risks, and runbook checks instead of becoming production-proven standalone patterns.

## Contradictions Resolved

- Liability-backed ERC4626 shares were kept separate from ordinary NAV-share vaults because `totalAssets()` reports protocol liability, not custodied inventory.
- Balance-sheet solvency gates were kept separate from account-level comptroller risk gates because the former constrains issuer solvency across assets and liabilities, not one borrower's collateralization.
- Domain-scoped bridge custody ledgers were kept separate from shared bridge lockboxes and sovereign balance trees: the reusable distinction is per-destination spendable accounting inside one escrow.
- USDT0 evidence is explicitly marked audit-source where no implementation code was present.
- Satoshi's risk-ordered redemption mechanics were not merged into rate-ordered redemption guidance because the ordering predicates differ.
