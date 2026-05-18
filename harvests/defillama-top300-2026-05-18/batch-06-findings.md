# Batch 06 Findings

Dry-run analyses were run against 8 additional source repositories. This batch focused on Uniswap V2/V4 AMM mechanics, Optimism bridge finality, tBTC Bitcoin custody, Fluid shared liquidity, and StakeWise V2 liquid-staking accounting.

## Source Repositories

| Protocol | Repository | Commit | Focus |
|----------|------------|--------|-------|
| Uniswap V2 | `Uniswap/v2-core` | `6a9e7c9` | constant-product pairs, reserve-delta accounting, cumulative TWAPs |
| Uniswap V2 | `Uniswap/v2-periphery` | `ed24991` | prepaid routers, route-scoped fee-on-transfer support, oracle helpers |
| Fluid Lending | `Instadapp/fluid-contracts-public` | `a9949b4` | shared liquidity core, progressive limits, selector proxy, resolvers |
| StakeWise V2 | `stakewise/contracts` | `29022d7` | principal/reward split tokens, reward routing, slashing accounting |
| Uniswap V4 | `Uniswap/v4-core` | `46c6834` | singleton flash accounting, hooks, custom deltas, dynamic fees |
| Uniswap V4 | `Uniswap/v4-periphery` | `9dafaae` | action routers, slippage checks, no-delegatecall and hook guardrails |
| Optimism Bridge | `ethereum-optimism/optimism` | `4a278fa` | retryable messenger ledger, dispute-game exits, shared ETH lockbox |
| tBTC v2 | `threshold-network/tbtc-v2` | `52c02d1` | threshold custody wallets, UTXO deposit reveal, Bitcoin SPV gates |

## Accepted Catalog Updates

- Added AMM patterns for constant-product reserve-delta swaps, V2 prepaid routing, singleton flash accounting, net-delta settlement invariants, address-encoded hook permissions, hook-returned custom accounting deltas, and hook-governed dynamic LP fees.
- Added Fluid-derived patterns for shared liquidity kernels, progressive per-protocol liquidity limits, selector-routed module proxies, read-only storage resolver facades, revert-encoded simulation quotes, compressed amount storage, and liquidation tick/branch gas risk.
- Added StakeWise-derived patterns and requirements for principal/reward split derivatives, index-to-distributor reward routing, and liquid-staking loss accounting.
- Added Optimism-derived bridge patterns for retryable cross-domain message ledgers, dispute-game gated withdrawal finality, bridge-owned mintable token pairs, and authorized shared bridge lockboxes.
- Added tBTC-derived bridge and monitoring patterns for threshold custody wallet lifecycle, self-describing UTXO deposit reveal, Bitcoin SPV state-transition gates, optimistic mint with debt reconciliation, and read-only signer proposal validation.
- Updated existing docs for V2 TWAP accumulators, route-scoped fee-on-transfer support, V2 pool factory/minimum liquidity evidence, Fluid callback netting and kinked-rate validation, V4 action-router slippage checks, bridge proof liveness/finality, bounded parameter changes, lazy reward zero-balance checkpointing, and same-block report settlement fences.
- Expanded `ANTIPATTERNS.md` with quote/execution formula drift, permissioned exit custody, trusted SPV relay boundaries, delta-derived liquidity slippage checks, hook periphery guardrails, and trust-list admin caveats.

## Rejected Or Merged Candidates

- Minimum liquidity, canonical AMM factory, spot-price manipulation, fee-on-transfer blindness, flash-swap callbacks, and missing deadline/slippage checks were merged into existing docs rather than added again.
- Concentrated liquidity, tick crossing, range fee snapshots, permit front-run griefing, approval persistence, multicall composition, full-precision rounding, absorbed liquidation inventory, and dust-aware liquidation caps were rejected as already covered.
- Optimism StandardBridge was not used as refund-fallback evidence because failed receiver execution is retry-oriented and can still require application-level recovery.
- tBTC fraud signatures were folded into the threshold custody lifecycle rather than treated as conclusive fraud by themselves.
- Fluid cooldown-based authorization was not treated as a timelock; it was documented only as weaker bounded-risk evidence.

## Contradiction Review

- Singleton and shared-liquidity patterns are documented as narrow exceptions to shared-pool warnings only when state is keyed, writers are restricted, and net-delta or core-ledger invariants are enforced.
- V4 hook permission bits are framed as capability declaration, not proof that a hook is trusted.
- V2 TWAPs are kept separate from V3 tick/harmonic-liquidity mechanics.
- Optimism proof/finalization pause behavior is documented as a liveness exception that needs scope, expiry, and monitoring, not as a generic exit-liveness pattern.
- tBTC deposit reveal is documented as discovery only; SPV sweep finalizes accounting. Its SPV proof docs also preserve the relay-maintainer trust boundary.
- StakeWise permissioned escrow is documented as a risk unless user entitlement, queue order, or migration trust is explicit.

## Verification

- Each source repository was inspected by a dry-run subagent using `skills/harvest-patterns/SKILL.md`.
- Existing catalog docs, `patterns/INDEX.md`, and `ANTIPATTERNS.md` were compared before accepting updates.
- Deployment dump files in Fluid were excluded because the local checkout reported a case-collision warning.
- Full catalog index regeneration and staged markdown validation were run before commit.
