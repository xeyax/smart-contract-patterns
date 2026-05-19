# Batch 28 Findings

Expanded source-discovery batch covering Silo V2, Puffer, StakeWise V3, Swell V3, Notional V3, Goldfinch, Origin Dollar, Fraxtal contracts, Alchemix V2, Moonwell V2, Term Finance, and Velodrome Superchain.

## Repositories

| Protocol | Repository | Commit |
|----------|------------|--------|
| Silo Finance | `silo-finance/silo-contracts-v2` | `fd1c73beafb7c81f77cd4477002ebadb4142d243` |
| Puffer Finance | `PufferFinance/puffer-contracts` | `380600060cd231fd8616ba167e674d4140486dbb` |
| StakeWise V3 | `stakewise/v3-core` | `31b2da5e9c729b00ead0db16369141608410bee8` |
| Swell V3 | `SwellNetwork/v3-core-public` | `ba1eeff12ab994a26492fa5dcd0aa8937733dbb4` |
| Notional V3 | `notional-finance/contracts-v3` | `ae20d99ebfb0b14cf7b08421722b85849fb11edf` |
| Goldfinch | `goldfinch-eng/mono` | `bb251675d8a28d046f4d4763e1cf8874ee7c2723` |
| Origin Dollar | `originprotocol/origin-dollar` | `cd7218c2b070a52470b2621c3ce0ce12378ba700` |
| Fraxtal Contracts | `FraxFinance/fraxtal-contracts` | `7bfce185a306c96170e03fdbd65ae4a1a3e6cb1c` |
| Alchemix V2 | `alchemix-finance/v2-foundry` | `8915ef7b1714c16f9e260a4ef41c5f254d5b7f58` |
| Moonwell V2 | `moonwell-fi/moonwell-contracts-v2` | `c0c65f8d1c1a968c952c1bff344f2906b15b86a7` |
| Term Finance | `term-finance/term-finance-contracts` | `262098c71578bbb9e54d6c2a8d2d88d112b9662a` |
| Velodrome Superchain | `velodrome-finance/superchain-contracts` | `c93c466a2fcd1fd9dc79ba569f6b81c42bb50d61` |

## Accepted New Patterns

- `patterns/lending/pattern-sealed-double-auction-term-lending.md` captures Term Finance's bid/offer locker and fixed-term auction clearing model.
- `patterns/lending/pattern-signed-fixed-maturity-fcash-ledger.md` captures Notional V3's signed fCash balances, ERC1155 ids, and maturity settlement.
- `patterns/lending/pattern-dual-mode-collateral-shares.md` captures Silo V2 protected collateral versus borrowable collateral share modes.
- `patterns/lending/pattern-tranched-credit-line-payment-waterfall.md` captures Goldfinch senior/junior credit-line repayment allocation.
- `patterns/lending/pattern-lazy-credit-amortization-index.md` captures Alchemix yield-credit debt amortization.
- `patterns/lending/pattern-tick-weighted-transmuter-redemption.md` captures Alchemix Transmuter V2 tick and accumulated-weight redemption accounting.
- `patterns/oracles/pattern-paid-early-oracle-update-liquidation.md` captures Moonwell's Chainlink OEV delayed-read and paid fresh-update liquidation wrapper.
- `patterns/tokens/pattern-account-scoped-rebasing-credit-ledger.md` captures Origin's rebasing/non-rebasing credit ledger and WOETH wrapper boundary.

## Merged Into Existing Patterns

- Puffer and Swell batch-finalized exits were merged into `patterns/vaults/pattern-operator-finalized-withdrawal-claim.md`.
- StakeWise and Origin cumulative queues were merged into `patterns/vaults/pattern-height-interval-redemption-queue.md`.
- StakeWise and Puffer loss/slashing exposure was merged into the liquid-staking and restaking requirements.
- StakeWise and Puffer reporter/guardian payload handling was merged into `patterns/oracles/pattern-threshold-reporter-consensus.md`.
- Silo max-LTV versus solvency oracle behavior was merged into `patterns/oracles/pattern-action-scoped-bounded-lending-prices.md`.
- Silo and Term liquidation evidence was merged into `patterns/lending/pattern-dust-aware-liquidation-cap.md`.
- Notional exposure caps were merged into `patterns/lending/pattern-reserve-exposure-caps.md`.
- Velodrome Superchain bridge, gauge, rate-limit, and escrow behavior was merged into cross-chain, rewards, and access-control patterns.
- Alchemix and Origin buffer/smoothing behavior was merged into withdrawal liquidity and locked-profit smoothing patterns.

## Anti-Pattern Updates

- `ANTIPATTERNS.md` now calls out Chainlink-compatible wrappers that synthesize timestamps or ignore stored heartbeat values.
- Pause guidance now explicitly covers batch-finalized exits and burn-to-claim queues.
- Hook/callback guidance now treats market/share-token/distributor `call` or `delegatecall` hooks as privileged execution surfaces.
- Unrestricted admin, governance arbitrary execution, approval persistence, unbounded iteration, EOA gates, and beacon blast-radius notes were tightened with evidence from the batch.

## Deferred Or Rejected Candidates

- Term serial repo-token contracts were merged as a variant of rolling fixed-maturity debt tokens rather than added as a standalone pattern.
- Silo isolated-market and Moonwell Compound-style controls overlapped existing lending-market and comptroller patterns.
- Fraxtal Optimism-portal and Velodrome LayerZero-style route settings overlapped the previous bridge batch; only fresh Superchain evidence was merged.
- Puffer, StakeWise, Swell, Origin, and Alchemix queue variants were merged into existing async queue and buffer patterns instead of creating duplicate vault patterns.
