# Batch 11 Findings

Expanded discovery continued beyond the original `best_source_repo` map and analyzed 9 additional public source repositories.

## Source Repositories

| Protocol | Repository | Commit | Focus |
|----------|------------|--------|-------|
| Euler V2 | `euler-xyz/euler-vault-kit` | `5b98b42` | Modular lending vaults, threshold configuration |
| Euler V2 | `euler-xyz/ethereum-vault-connector` | `b9d557a` | Batch execution, deferred account/vault checks, subaccounts |
| M0 | `m0-foundation/protocol` | `b42fe5b` | Continuous indexes, validator-signed collateral reports |
| PancakeSwap AMM V2 | `pancakeswap/pancake-swap-core` | `3b21430` | Constant-product AMM core |
| PancakeSwap AMM V2 | `pancakeswap/pancake-swap-periphery` | `d769a6d` | Fee-on-transfer routing, sliding-window TWAPs |
| Polymarket International | `Polymarket/ctf-exchange` | `ed5c770` | Typed signed orders, outcome-token settlement |
| Lombard LBTC | `lombard-finance/evm-smart-contracts` | `5ec153c` | Cross-chain mint validation ledgers |
| mETH Protocol | `mantle-lsp/contracts` | `afa686b` | Reporter quorum, finalized oracle ranges, delayed unstake |
| Bedrock uniBTC | `bedrock-technology/uniBTC` | `1c474cb` | Reserve-gated minting, delayed multi-asset redemptions |

## Accepted Catalog Updates

- Added `patterns/lending/pattern-deferred-status-check-frame.md`.
- Added `patterns/access-control/pattern-address-prefix-subaccount-namespace.md`.
- Added `patterns/math/pattern-bounded-continuous-compounding-index.md`.
- Added `patterns/routing/pattern-typed-signed-order-settlement.md`.
- Added `patterns/routing/risk-zero-consideration-signed-order.md`.
- Added `patterns/liquidity/pattern-complementary-outcome-netting.md`.
- Updated collateral-threshold requirements with immediate borrow reduction plus liquidation-threshold ramp-down semantics.
- Updated break-glass and oracle-staleness guidance so pure risk-reducing setters are not blocked by stale oracle reads.
- Updated threshold reporter consensus and oracle reliability with reporter timestamp, report-window continuity, and quarantine guidance.
- Updated router, TWAP, ERC-1271, request-hash, async-exit, reserve-backing, and withdrawal-buffer docs with accepted variants.

## Rejected Or Merged Candidates

- PancakeSwap V2 AMM core mechanics were merged into existing constant-product, factory, minimum-liquidity, callback, and reserve-delta docs instead of creating duplicate patterns.
- Euler static module dispatch was not added as a standalone pattern; it overlaps existing selector/module proxy guidance.
- Euler transient-storage prewarming was rejected as gas-specific implementation detail.
- M0 freeze, penalty, and deactivation mechanics were rejected as mostly protocol-specific monetary policy.
- Lombard weighted validator-set proofs were merged into existing validator-set header guidance.
- Bedrock CCIP peer allowlists and failed-message handling were treated as overlaps with canonical counterpart validation and retryable-message caveats.

## Contradiction Review

- Euler's equality between borrow and liquidation LTV is documented as a no-grace-buffer mode, not as a replacement for the catalog's stricter default threshold gap.
- Oracle fail-closed guidance is preserved for value-bearing actions; stale-read exemptions are scoped only to monotonic risk reductions that do not need the price.
- Polymarket zero-consideration behavior is captured as a risk with an explicit "unless intended" boundary.
- Lombard's validation ledger is not presented as a full chain-bound hash schema because its mint id does not bind every source-domain field.
- Mantle reporter quorum remains partial oracle reliability; finality, continuity, bounds, and quarantine are separate requirements.
- Bedrock reserve checks are scoped to reserve-gated mint paths with configured feeds, not all custodial minting.

## Verification

- Dry-run harvest subagents compared candidates against the current catalog before edits.
- Catalog index regeneration and staged markdown validation were run before commit.
