# Batch 04 Findings

Dry-run analyses were run against 7 additional cloned repositories. This batch expanded the catalog into AMM/liquidity mechanics while adding targeted lending, rewards, governance, oracle, upgrade, routing, and token-integration entries.

## Repositories Analyzed

| Protocol | Repository | Main Accepted Themes |
|----------|------------|----------------------|
| Sky Lending | `sky-ecosystem/dss` | isolated core ledger, liquidation auctions, shutdown state machine |
| SSV Network | `ssvlabs/ssv-contracts` | indexed Merkle airdrops, vesting escrows, gas-DoS caveats |
| Curve DEX | `curvefi/curve-contract` | stable-swap invariant, invariant-delta LP accounting, virtual price |
| Compound V3 | `compound-finance/comet` | single-base lending, collateral thresholds, bridged governance, extension delegates |
| Uniswap V3 | `Uniswap/v3-core`, `Uniswap/v3-periphery` | concentrated liquidity, callback settlement, fee snapshots, AMM risks |
| PancakeSwap AMM | `pancakeswap/pancake-v3-contracts` | CL factory/routing corroboration, range rewards, tick gas risk |
| Venus Core Pool | `VenusProtocol/venus-protocol` | action-scoped bounded prices, diamond selector collision, debt-converting flash loans |

## Catalog Changes Accepted

- Added a liquidity category for stable-swap and concentrated-liquidity AMMs: amplified invariants, invariant-delta LP accounting, virtual-price requirements, off-peg dynamic fees, concentrated-liquidity range accounting, canonical pool factories, callback settlement, fee-growth snapshots, and AMM-specific risks.
- Added lending patterns and requirements for liquidation caps, resettable Dutch liquidation auctions, single borrow-asset markets, collateral threshold separation, protocol-absorbed liquidation inventory, and debt-converting flash loans.
- Added rewards patterns for indexed Merkle airdrops, isolated vesting escrows, and range-liquidity reward indexes.
- Added governance, cross-chain, upgrade, math, routing, token-integration, access-control, and oracle entries for global settlement, bridged governance receivers, extension delegates, diamond selector collision risk, full-precision rounding, stateless swap routers, adapter-isolated ledgers, bounded timelocked parameters, and action-scoped bounded lending prices.
- Updated existing docs for lending freshness, reserve caps, bounded inflation, multi-kink rate curves, TWAP harmonic mean liquidity, exchange-rate valuation, Merkle alternatives, pause scope, victim-appendable unbounded iteration, donation sweep ordering, silent governance changes, delegatecall context, and payable multicall value reuse.

## Rejected or Merged Candidates

- Uniswap and PancakeSwap overlapping concentrated-liquidity findings were merged into one `patterns/liquidity/` family instead of separate `amm` and `liquidity` duplicates.
- TWAP basics, permit front-run handling, queued reward streaming, balance-delta transfers, slippage/deadline checks, fee-on-transfer assumptions, broad owner/admin risks, and generic reentrancy locks were rejected as already covered.
- Curve proportional withdrawal and token-normalization observations were treated as evidence for existing docs, not standalone entries.
- Venus restricted liquidations and debt migration delegates were deferred as too project-specific without more comparative evidence.
