# Batch 08 Findings

Dry-run analyses were run against 8 additional source candidates. This batch was deliberately conservative because several DefiLlama source-map matches were staking, wallet, token, or educational repos rather than the protocol category implied by the row.

## Source Repositories

| Protocol | Repository | Commit | Focus |
|----------|------------|--------|-------|
| UniRouter Bridge | `UniRouter/unirouter-staking-contract` | `ddd8383` | staking points; rejected as bridge source |
| Coinbase Wrapped Staked ETH | `coinbase/smart-wallet` | `e7fde11` | ERC-4337 wallet signatures; rejected as cbETH source |
| B2 Buzz | `b2network/halving-protocol` | `3d0316b` | halving token; rejected as bridge source |
| b14g | `b14glabs/btc-signature-verify` | `b5df0ee` | educational BTC key proof; weak restaking evidence |
| AFI Protocol | `Artificial-Financial-Intelligence/afiUSD` | `dc68ea2` | ERC4626 yield vault, cooldown exits, reported profit/loss fees |
| GAIB | `gaib-ai/symbiotic-super-sum` | `d94e056` | Symbiotic-backed LayerZero DVN simulation |
| OnRe | `onre-finance/jup-onyc-integration` | `9dc6491` | Solana/Jupiter RWA integration adapter |
| KPK | `karpatkey/kpk-token` | `5d45c13` | launch-locked governance token and transfer budgets |

## Accepted Catalog Updates

- Added account and wallet signature patterns for ERC-1271 replay-safe account signatures and scoped chain-id bypass for wallet maintenance, using Coinbase Smart Wallet as non-LST but reusable wallet evidence.
- Added a cross-chain pattern for stake-backed DVN verifier adapters, with GAIB marked as simulation-grade evidence rather than production-proven bridge infrastructure.
- Added a token pattern for launch-locked recipient-scoped transfer gates from KPK's non-transferable launch and budgeted-transfer design.
- Updated high-water-mark fee docs with AFI-derived caveats for fee-share reserves and clawback under later losses.
- Updated operation-cadence monitoring with cross-chain verifier-worker persistence, packet status, proof, retry, and execution monitoring.
- Updated transfer-permission, Solana account validation, math, and anti-pattern docs with delegated-spender policy, raw layout discriminator checks, denominator/narrowing-cast checks, overwrite-based allowance changes, and EIP-7702 delegate context caveats.

## Rejected Or Merged Candidates

- UniRouter, B2 Buzz, Coinbase cbETH, and b14g were rejected as protocol-category source matches for bridge, liquid-staking, or restaking behavior.
- UniRouter fee-on-transfer rejection, CEI, and unbounded stake-history loops were rejected as already covered by existing token-integration and unbounded-iteration guidance.
- B2 deterministic halving emission was merged conceptually into bounded inflation but rejected as too thin and untested for a new doc.
- b14g BTC signature verification was rejected as production evidence because it is educational, uses a mock public-key source, and does not prove Bitcoin transaction or staking inclusion.
- OnRe APR interval pricing, Token-2022 metadata, and adapter quote behavior were rejected as standalone docs because the source is an integration adapter with light tests.

## Contradiction Review

- Coinbase chain-id bypass is framed as a narrow smart-wallet maintenance exception, not a contradiction to chain-bound bridge request hashes or signature-scope requirements.
- GAIB's DVN verifier adapter is one externally secured verifier path, not multi-adapter message quorum.
- KPK's launch lock is not an emergency pause or vault exit pattern; using it for redeemable claims would conflict with `Pause Traps Funds`.
- AFI fee-share burning is not presented as HWM. It is a provisional reserve/clawback caveat that fails if fee shares can leave before later losses.
- OnRe adapter quote math reinforces quote/execution drift risks rather than proving zero-impact pricing is enough for user protection.

## Verification

- Each source repository was inspected by a dry-run subagent using `skills/harvest-patterns/SKILL.md`.
- Existing catalog docs, `patterns/INDEX.md`, and `ANTIPATTERNS.md` were compared before accepting updates.
- Weak source-map matches were recorded as rejected instead of being forced into catalog docs.
- Full catalog index regeneration and staged markdown validation were run before commit.
