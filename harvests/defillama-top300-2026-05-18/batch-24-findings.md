# Batch 24 Findings

## Source Repositories

| Protocol | Repository | Commit | Focus |
|----------|------------|--------|-------|
| Kamino Vault | `Kamino-Finance/kvault` | `ac367c3adecf9ae29e384b50c9cf2e7fcc521f94` | Lending-reserve vault allocation |
| Kamino Farms | `Kamino-Finance/kfarms` | `2a63e5ab59629c77f8b4043781c1e4b4572c7b60` | Piecewise farm reward indexes |
| Kamino Scope | `Kamino-Finance/scope` | `3eb930312386bdba39c540e62d863ce24bc4c492` | Multi-source oracle aggregation |
| Kamino Distributor | `Kamino-Finance/distributor` | `aecda23a7363f448fae37543ab5a9f4662e50e50` | Merkle seeded vesting claims |
| Kamino Liquidity SDK | `Kamino-Finance/kliquidity-sdk` | `99c3213254700e953f9704a90fa09bb2ad38ca09` | Liquidity integration SDK |
| Kamino Farms SDK | `Kamino-Finance/farms-sdk` | `aa82c580734ddd971a0aa52ade70c46fff2bcf68` | Farms integration SDK |
| Kamino Lending SDK | `Kamino-Finance/klend-sdk` | `573d0bf52421cf22e930a5a4d73d1722a36ad6d9` | Lending integration SDK |
| Kamino Limo | `Kamino-Finance/limo` | `575e0e22eceefac7f9ccdb76e1ff85210466b525` | Instruction-paired flash order settlement |
| Kamino Limo SDK | `Kamino-Finance/limo-sdk` | `e7369cb238f9c55f5addccbaa1e48d3bfdc9c5e7` | Limit-order SDK integration |
| Sanctum Unstake Program | `igneous-labs/sanctum-unstake-program` | `b6db89b0d39e8ff798171331dd6f8d120dbc9327` | Instant unstake reserve accounting |
| Sanctum INF 1.5 | `igneous-labs/inf-1.5` | `29dbbd47e822e5e3fbcc5a2e2190f00dd4e075be` | Multi-LST accounting and rebalancing |
| Sanctum INF Jupiter Interface | `igneous-labs/inf-jup-interface` | `3f14e9936878916c71213d0cba66e7ad19432728` | Adapter quote/execution parity |
| Sanctum SPL Stake Pool | `igneous-labs/sanctum-spl-stake-pool` | `81f7e922a4cad340da8347a2ef244445d0cc3e26` | Stake-pool reference |
| Sanctum SPL Stake Pool SDK | `igneous-labs/sanctum-spl-stake-pool-sdk` | `5f8d7ea24ce7ea504068ff8781a322c304b58e90` | Stake-pool SDK integration |
| Sanctum SPL Stake Pool CLI | `igneous-labs/sanctum-spl-stake-pool-cli` | `8b9e163dde5999b07cf82d9783084b5a1beafbb4` | Stake-pool admin CLI |
| Sanctum Flatslab CLI | `igneous-labs/flatslab-cli` | `f88aeb6c5c0eb157f38edae622d633f6f2a14d32` | Pricing/admin CLI |
| Solana Perpetuals | `solana-labs/perpetuals` | `ebfb4972ea5d1cde8580a7e8c7b9dbd1fdb2b002` | Pool-backed perpetuals reference |

`jup-ag/perpetuals` was unavailable or private during this batch and is not counted.

## Accepted Catalog Updates

- Added [Instruction-Paired Flash Order Settlement](../../patterns/routing/pattern-instruction-paired-flash-order-settlement.md), [Merkle-Seeded Linear Vesting Claim Ledger](../../patterns/rewards/pattern-merkle-seeded-linear-vesting-claim-ledger.md), [Instruction-Paired Rebalance Solvency Record](../../patterns/liquidity/pattern-instruction-paired-rebalance-solvency-record.md), and [Initial And Maintenance Leverage Gates](../../patterns/perps/pattern-initial-maintenance-leverage-gates.md).
- Updated vault allocator and withdrawal-buffer guidance with Kamino KVault reserve caps, Sanctum instant-unstake incoming-stake liabilities, utilization-sensitive unstake fees, and flash-borrowed reserve accounting.
- Updated reward, oracle, and access-control docs for piecewise reward-rate indexes, most-recent agreement oracles, freshness-preserving composite oracle graphs, scoped pause matrices, and Solana account cohort validation caveats.
- Updated LST router, LP virtual-price, locked-profit, simulation-quote, perps PnL, ADL reserve, and read-only health-check docs with Sanctum INF and Solana Perpetuals evidence.
- Updated anti-pattern guidance for flash-order slippage settlement and adapter quote/execution parity.

## Rejected Or Deferred Candidates

- Plain Merkle airdrop mechanics, post-deadline clawback, PDA authority checks, token CPI checks, and basic fee mechanics were duplicates of existing catalog guidance.
- Kamino SDK findings were kept as lower-confidence corroboration because they mostly show client-side assembly, account derivation, quote preflight, and slippage-bound transaction construction.
- Sanctum SPL stake-pool reference, SDK, and CLI findings were treated as integration or operational evidence rather than new on-chain pattern sources.
- Sanctum generic upgrade-slot-pinned calculator validation was not accepted because the inspected commit itself marks the generic verification as incomplete.
- Flatslab negative-fee CSV pricing and admin CLI simulation/dump flows were left as operational tooling notes, not reusable smart-contract patterns.
- Solana Perpetuals liquidation behavior is threshold-based, not a progressive liquidation state machine, so no progressive-liquidation update was made.

## Contradictions And Caveats

- SDK and CLI repositories can validate integration ergonomics, but they do not replace on-chain account, slippage, owner, or PDA checks in the catalog.
- Instruction-paired settlement and rebalancing depend on Solana instruction sysvar semantics and strict interstitial instruction restrictions; the pattern should not be generalized to chains without equivalent same-transaction introspection.
- Kamino Distributor's reusable lesson is Merkle-seeded vesting state. Implementations should still bind leaf domains to distributor, mint, and version because weak leaf domain separation contradicts Merkle guidance elsewhere in the catalog.
- Sanctum INF's configured calculators preserve accounting value under selected calculators, not market liquidation value. The catalog keeps this separate from oracle collateral valuation.
- Solana Perpetuals adds useful initial/maintenance leverage and payoff-cap evidence, but it does not satisfy ADL or progressive liquidation requirements by itself.
