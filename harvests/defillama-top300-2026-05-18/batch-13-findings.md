# Batch 13 Findings

Expanded discovery analyzed 22 additional public source repositories across bridges, CDPs, lending markets, Move/Solana lending, AMMs, gauges, LST exits, and vault systems.

## Source Repositories

| Protocol | Repository | Commit | Focus |
|----------|------------|--------|-------|
| Axelar | `axelarnetwork/axelar-cgp-solidity` | `1736bfa` | Gateway approval binding and weighted operator rotation |
| Hyperlane | `hyperlane-xyz/hyperlane-monorepo` | `748379e` | Recipient-scoped message verification and bridge hook approvals |
| zkSync Era txBridge | `matter-labs/zksync-era` | `3f99eb0` | Gateway message roots and failed-deposit recovery |
| Linea Bridge | `Consensys/linea-monorepo` | `eb32ea8` | Rolling message hashes, sparse roots, and directional pauses |
| Agglayer | `agglayer/agglayer-contracts` | `110bda5` | Global exit roots and callback-safe nullifiers |
| Stargate V2 | `stargate-protocol/stargate-v2` | `8c41a96` | Deferred; shallow HEAD confirmation only |
| Compound V2 | `compound-finance/compound-protocol` | `a3214f6` | Comptroller gates and lazy borrow indexes |
| Liquity V1 | `liquity/dev` | `3e64ee1` | Stability-pool product/sum accounting and sorted troves |
| Liquity V2 | `liquity/bold` | `3fcaf60` | Rate-ordered redemptions and position manager permissions |
| crvUSD | `curvefi/curve-stablecoin` | `8a98f20` | Band-ranged soft liquidation |
| Yearn V3 | `yearn/yearn-vaults-v3` | `104a2b2` | Deferred; mapped for later profit-unlocking review |
| Mellow Core | `mellow-finance/mellow-vaults` | `157a0b4` | Deferred; mapped for later aggregate-vault review |
| Suilend | `suilend/suilend` | `d5ba83a` | Move rate limits and action-scoped stale-price exits |
| Save/Solend | `solendprotocol/solana-program-library` | `d04ce00` | Solana flash-loan instruction pairing and outflow limits |
| NAVI Lending | `naviprotocol/navi-smart-contracts` | `473b093` | Move receipt-bound flash loans and oracle warning states |
| Blend Pools V2 | `blend-capital/blend-contracts-v2` | `ba22b48` | Deferred; mapped for later backstop and auction review |
| Aerodrome V1 | `aerodrome-finance/slipstream` | `f8717fa` | TWAP-deviation fees and gauge emission caps |
| PancakeSwap Infinity Core | `pancakeswap/infinity-core` | `7c04695` | Bin liquidity books and shared vault settlement |
| PancakeSwap Infinity Periphery | `pancakeswap/infinity-periphery` | `f39aef4` | Signed hook-delta slippage and permit-forwarding caveats |
| Frax Ether | `FraxFinance/frxETH-v2-public` | `83dfe93` | Partial LST redemption-ticket review |
| fx Protocol | `AladdinDAO/fx-protocol-contracts` | `5e198e9` | Deferred; shallow map only |
| QuickSwap Periphery | `QuickSwap/quickswap-periphery` | `522a941` | Deferred; likely V2-router overlap |

## Accepted Catalog Updates

- Added new docs for Move receipt-bound flash loans, stability-pool product/sum accounting, hint-assisted sorted CDP lists, rate-ordered redemptions, position-scoped managers, band-ranged soft liquidation AMMs, TWAP-deviation dynamic fees, capped gauge emission redistribution, discrete price-bin liquidity books, recipient-scoped message verifiers, and domain-scoped message root accumulators.
- Updated lending docs for Solana flash-loan repay matching, progressive outflow limits, comptroller gates, lazy borrow indexes, and accounting freshness.
- Updated oracle docs for stale-price exit scopes, time-bound warning states, historical min/max bounds, and history-span validation.
- Updated liquidity docs for app-scoped shared vault settlement and signed hook-delta slippage checks.
- Updated bridge and governance docs for Axelar-style approval binding, weighted operator-set epochs, failed-deposit reclaim proofs, directional pauses, and root-based claim nullifiers.
- Updated vault exit docs for NFT redemption tickets and partial LST redemptions.
- Updated `ANTIPATTERNS.md` for per-call bridge hook approvals, permit-forwarding grief resistance, callback-wide reentrancy assumptions, bridge callback nullifiers, and `tx.origin`-keyed economic entitlement hazards.

## Rejected Or Deferred Candidates

- Stargate V2, Yearn V3, Mellow, Blend, AladdinDAO fx, and QuickSwap Periphery need targeted follow-up before making catalog claims.
- Compound kinked utilization, pause guardian, and borrow caps were merged into existing lending and access-control docs instead of new pages.
- Liquity V1 price-feed fallback and recovery-mode liquidation were treated as oracle and liquidation caveats rather than new standalone docs.
- Liquity V2 stability-pool mechanics were merged into the Liquity V1 stability-pool doc.
- Curve ERC4626 donation, zero-share, and flash-loan debt ceiling findings overlapped existing vault and lending risk docs.
- Aerodrome CL staking reward indexing overlapped existing range-liquidity reward guidance.
- Pancake Infinity hook permissions and dynamic hook fees overlapped existing Uniswap V4-derived hook docs.
- Frax validator-credit, operator-registry, and router details were not accepted because the subagent inspected only the redemption queue deeply enough.

## Contradiction Review

- Move receipt-bound flash loans are scoped to Move resource semantics and do not replace Solana instruction-paired or EVM debt-converting flash-loan patterns.
- Product/sum stability-pool accounting is framed as a pooled liquidation backstop, not general reward accounting.
- Rate-ordered redemptions are documented as a borrower-pricing mechanism with same-rate and churn caveats, not as universally fair liquidation ordering.
- TWAP-deviation dynamic fees reduce adverse selection but do not prove oracle accuracy.
- Recipient-scoped message verification does not make the mailbox uniformly safe; weak recipient verifiers remain a recipient-level risk.
- Domain-scoped root accumulators require authenticated root writers and exact-once nullifiers; root compression is not source-chain finality by itself.
- Directional bridge pauses are a liveness recommendation, not a promise that every emergency can leave every exit path open.

## Verification

- Dry-run harvest subagents compared candidates against the catalog and anti-patterns before edits.
- Catalog index regeneration and staged markdown validation were run before commit.
