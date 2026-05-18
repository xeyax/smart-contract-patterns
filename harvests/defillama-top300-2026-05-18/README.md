# DefiLlama Top 300 Harvest — 2026-05-18

Source snapshot: `https://api.llama.fi/protocols`, sorted by descending `tvl`.

## Scope

- Protocols inspected from DefiLlama snapshot: 300.
- Entries with direct `github` metadata in DefiLlama: 40.
- GitHub handles queried for source candidates: 41.
- Candidate repository rows found by metadata scoring: 235.
- First cloned source batch: 12 repositories.

## First Batch Repositories

| Protocol | Repository | Category |
|----------|------------|----------|
| Lido | `lidofinance/core` | Liquid Staking |
| EigenCloud | `Layr-Labs/eigenlayer-contracts` | Restaking |
| Pendle | `pendle-finance/pendle-core-v2-public` | Yield |
| Veda | `Veda-Labs/boring-vault` | Onchain Capital Allocator |
| Symbiotic | `symbioticfi/core` | Restaking |
| Enzyme Finance | `enzymefinance/protocol` | Indexes |
| Renzo | `Renzo-Protocol/contracts-public` | Liquid Restaking |
| Beefy | `beefyfinance/beefy-contracts` | Yield Aggregator |
| Nexus Mutual | `NexusMutual/smart-contracts` | Insurance |
| Reserve Protocol | `reserve-protocol/reserve-index-dtf` | Indexes |
| Rocket Pool | `rocket-pool/rocketpool` | Liquid Staking |
| Function FBTC | `fbtc-xyz/fbtc-contract` | Bridge |

## Files

- `top300-source-map.csv` — top-300 protocol map with DefiLlama metadata and best GitHub source candidate when available.

## Notes

DefiLlama's top-300 by TVL includes centralized exchanges, RWAs, bridges, and other projects where public smart-contract source may be absent or not discoverable from DefiLlama metadata. The harvest uses direct DefiLlama GitHub metadata first and treats name-based GitHub repository matches as candidates requiring code inspection before catalog updates.
