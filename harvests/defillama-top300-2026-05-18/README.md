# DefiLlama Top 300 Harvest — 2026-05-18

Source snapshot: `https://api.llama.fi/protocols`, sorted by descending `tvl`.

## Scope

- Protocols inspected from DefiLlama snapshot: 300.
- Entries with direct `github` metadata in DefiLlama: 40.
- GitHub handles queried for source candidates: 41.
- Candidate repository rows found by metadata scoring: 235.
- Source repositories analyzed so far: 46 repositories across 6 batches.

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

## Second Batch Repositories

| Protocol | Repository | Category |
|----------|------------|----------|
| WBTC | `WrappedBTC/bitcoin-token-smart-contracts` | Bridge |
| JustLend | `justlend/justlend-protocol` | Lending |
| Portal | `wormhole-foundation/wormhole-ntt-contracts` | Bridge |
| Spiko | `spiko-tech/contracts` | RWA |
| Convex Finance | `convex-eth/frax-cvx-platform` | Yield |
| cap | `cap-labs-dev/cap-contracts` | Lending |

## Third Batch Repositories

| Protocol | Repository | Category |
|----------|------------|----------|
| Aave | `aave-dao/aave-v3-origin` | Lending |
| Morpho Blue | `morpho-org/morpho-blue` | Lending |
| SparkLend | `sparkdotfi/sparklend-advanced` | Lending |
| ether.fi | `etherfi-protocol/smart-contracts` | Liquid Restaking |
| Ethena | `ethena-labs/bbp-public-assets` | Stablecoin |
| Maple Finance | `maple-labs/maple-core-v2` | Lending |

## Fourth Batch Repositories

| Protocol | Repository | Category |
|----------|------------|----------|
| Sky Lending | `sky-ecosystem/dss` | CDP |
| SSV Network | `ssvlabs/ssv-contracts` | Staking Pool |
| Curve DEX | `curvefi/curve-contract` | DEX |
| Compound V3 | `compound-finance/comet` | Lending |
| Uniswap V3 | `Uniswap/v3-core`, `Uniswap/v3-periphery` | DEX |
| PancakeSwap AMM | `pancakeswap/pancake-v3-contracts` | DEX |
| Venus Core Pool | `VenusProtocol/venus-protocol` | Lending |

## Fifth Batch Repositories

| Protocol | Repository | Category |
|----------|------------|----------|
| Kamino Lend | `Kamino-Finance/klend` | Lending |
| Centrifuge Protocol | `centrifuge/liquidity-pools` | RWA |
| Raydium AMM | `raydium-io/raydium-amm` | DEX |
| Arbitrum Bridge | `OffchainLabs/token-bridge-contracts` | Canonical Bridge |
| Polygon Bridge | `maticnetwork/pos-portal` | Bridge |
| Ondo Yield Assets | `code-423n4/2024-03-ondo-finance` | RWA audit snapshot |

## Sixth Batch Repositories

| Protocol | Repository | Category |
|----------|------------|----------|
| Uniswap V2 | `Uniswap/v2-core`, `Uniswap/v2-periphery` | DEX |
| Fluid Lending | `Instadapp/fluid-contracts-public` | Lending |
| StakeWise V2 | `stakewise/contracts` | Liquid Staking |
| Uniswap V4 | `Uniswap/v4-core`, `Uniswap/v4-periphery` | DEX |
| Optimism Bridge | `ethereum-optimism/optimism` | Canonical Bridge |
| tBTC v2 | `threshold-network/tbtc-v2` | Bridge |

## Files

- `top300-source-map.csv` — top-300 protocol map with DefiLlama metadata and best GitHub source candidate when available.
- `batch-01-findings.md` — accepted and deferred catalog updates from the first 12 dry-run analyses.
- `batch-02-findings.md` — accepted and deferred catalog updates from the next 6 dry-run analyses.
- `batch-03-findings.md` — accepted and deferred catalog updates from the next 6 dry-run analyses.
- `batch-04-findings.md` — accepted and deferred catalog updates from the next 7 dry-run analyses.
- `batch-05-findings.md` — accepted and deferred catalog updates from the next 6 dry-run analyses.
- `batch-06-findings.md` — accepted and deferred catalog updates from the next 8 source repositories.

## Notes

DefiLlama's top-300 by TVL includes centralized exchanges, RWAs, bridges, and other projects where public smart-contract source may be absent or not discoverable from DefiLlama metadata. The harvest uses direct DefiLlama GitHub metadata first and treats name-based GitHub repository matches as candidates requiring code inspection before catalog updates.
