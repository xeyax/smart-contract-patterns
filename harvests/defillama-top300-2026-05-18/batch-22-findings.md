# Batch 22 Findings

## Source Repositories

| Protocol | Repository | Commit | Focus |
|----------|------------|--------|-------|
| Jupiter AMM Implementation | `jup-ag/jupiter-amm-implementation` | `cc068c9d1df0060c62f9a8a4fc37ea13ea7b9b39` | AMM snapshot simulation, sharded route authorities |
| Jupiter CPI | `jup-ag/jupiter-cpi` | `12bc5f67b94a2c3edc74d6e721a19442124a0bad` | Router authority interface |
| Jupiter Lock | `jup-ag/jup-lock` | `f1535b4067b1d90fd682edc94ac693496b0a9812` | Merkle vesting escrows, Token-2022 escrow lifecycle |
| Meteora Dynamic Bonding Curve | `MeteoraAg/dynamic-bonding-curve` | `b4f954733f0e88258f1eb3f0eff75e4314c9610c` | Launch fee fragmentation guard, AMM migration |
| Meteora Presale | `MeteoraAg/presale` | `2acd7c9c20bada425e9ff493260be4328b350b57` | Merkle sale caps, pro-rata refunds, Token-2022 deposits |
| Meteora Zap Program | `MeteoraAg/zap-program` | `c8dd95b4327158320238e2c4094507ab33883830` | Zap residual ledger, adjacent-instruction settlement guard |
| Meteora Dynamic Fee Sharing | `MeteoraAg/dynamic-fee-sharing` | `f9be4a9a94cf21f1955344bd459eb120e0c8d5af` | CPI fee harvest, balance-delta reward funding |
| Meteora Vault Periphery | `MeteoraAg/vault-periphery` | `2ad44b6d823fb3547d0e9c893d356fafc2130bce` | Periphery integration review |
| Midas Protocol | `Midas-Protocol/contracts` | `352be0e9ba2795e14d05a5fa4661cb2569655141` | Lending / diamond-extension review |
| EtherFi Cash Contracts | `etherfi-protocol/cash-contracts` | `c270e3b0f1606ecfaf6ba958068cb920b367f7f6` | Chain-scoped idempotent top-up settlement |
| EtherFi weETH Cross-Chain | `etherfi-protocol/weETH-cross-chain` | `cc6c220847217df8f9dcc4ba19c1c349106a002c` | Pairwise bridge limits, optimistic sync deficits |
| EtherFi Cash V3 | `etherfi-protocol/cash-v3` | `e05bda2be27a6a606f3f1b8ff0d0791032fd0ff8` | Modular wallet solvency hooks, base-asset oracle registry |
| EtherFi AVS Smart Contracts | `etherfi-protocol/avs-smart-contracts` | `50b221736873a75ed03cebde884aa8cf519cf3cc` | Selector-scoped operator routing |
| EtherFi beHYPE | `etherfi-protocol/beHYPE` | `06ee135254508fa3f0ab6b1bd8e80dc805884420` | Staking-core cooldowns, low-watermark withdrawals |
| Yearn Tokenized Strategy | `yearn/tokenized-strategy` | `9ef68041bd034353d39941e487499d111c3d3901` | Strategy accounting corroboration |
| Yearn Tokenized Strategy Periphery | `yearn/tokenized-strategy-periphery` | `1e889550bb97fb65386d1ac02f993265bc0cb541` | Health checks, triggers, reward-token auctions |
| Yearn Vault Periphery | `yearn/vault-periphery` | `bc4eee4051e3319427012e65296110bbdc00488d` | Debt allocator, accountant corroboration |

## Accepted Catalog Updates

- Added [Merkle-Instantiated Vesting Escrow Factory](../../patterns/rewards/pattern-merkle-instantiated-vesting-escrow-factory.md), [Bonding-Curve Terminal Liquidity Cutover](../../patterns/liquidity/pattern-bonding-curve-terminal-liquidity-cutover.md), [Pairwise Bridge Rate Limits](../../patterns/cross-chain/pattern-pairwise-bridge-rate-limits.md), [Read-Only Keeper Trigger Facade](../../patterns/automation/pattern-read-only-keeper-trigger-facade.md), [Hysteretic Strategy Debt Allocator](../../patterns/vaults/pattern-hysteretic-strategy-debt-allocator.md), [Merkle-Scoped Sale Escrow Caps](../../patterns/access-control/pattern-merkle-scoped-sale-escrow-caps.md), and [Oversubscribed Pro-Rata Sale Escrow](../../patterns/tokens/pattern-oversubscribed-pro-rata-sale-escrow.md).
- Updated PDA authority sharding, Merkle domain separation, Token-2022 escrow lifecycle, launch fee fragmentation guards, adjacent-instruction settlement, optimistic bridge debt, modular wallet deferred solvency checks, base-asset oracle depth limits, NAV report overrides, staking-core cooldowns, selector-scoped operator routing, chain-scoped idempotency, withdrawal buffer, operator-finalized claims, reward auctions, lazy reward indexes, balance-delta funding, zap residual accounting, participant permission bits, and anti-pattern guidance.
- Added anti-pattern refinements for claim pauses, Token-2022 and CPI actual-received accounting, ledger-backed zaps without per-leg minimums, snapshot-simulated quote parity, external CPI reward harvests, and transfer-hook remaining-account validation.

## Rejected Or Deferred Candidates

- `pump-fun/transfer-hook-authority` at `d5664eeb0dd13afe25f77b119ffd8425a23bfbaf` was not counted because the inspected Anchor module did not contain reusable on-chain logic.
- `MeteoraAg/vault-periphery` was counted as source-bearing integration code, but no standalone pattern was added; its useful lesson is deferred to periphery integration caution.
- `Midas-Protocol/contracts` maps mostly to existing diamond, selector-scope, lending, and risk-gate docs; no stronger standalone candidate was accepted in this batch.
- `yearn/tokenized-strategy` corroborates existing locked-profit, two-step-authority, and namespaced-storage guidance, while the reusable new mechanics came from Yearn periphery.
- Several EtherFi product repos were used as evidence for existing docs rather than as standalone pattern sources.

## Contradictions And Caveats

- Route and instruction-introspection guards prevent orphaned settlement calls, but they do not replace user slippage bounds.
- Pairwise bridge rate limits reduce route blast radius, but they can delay legitimate exits; bridge liveness and pause guidance remain relevant.
- Selector-scoped routers do not constrain sensitive calldata unless selectors are paired with target and argument manifests; privileged manager bypasses remain trusted paths.
- Merkle-root patterns require domain-separated leaf and internal-node hashing, and tree generation remains an off-chain trust boundary.
- Empty or placeholder public repositories are not counted toward the source-bearing inspection ledger.
