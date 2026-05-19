# Batch 21 Findings

## Source Repositories

| Protocol | Repository | Commit | Focus |
|----------|------------|--------|-------|
| VVS Swap Core | `vvs-finance/vvs-swap-core` | `31a9c67ee0ff37cdce02c26c0354053128c5d8fe` | Uniswap V2-style AMM mechanics |
| VVS Swap Periphery | `vvs-finance/vvs-swap-periphery` | `2c55492bd21949c04f51781c6de1aa5eb75be7e6` | Router, migrator, fee-on-transfer swaps |
| VVS Farm | `vvs-finance/vvs-farm` | `acd79b99d88157b9d520eeac92e8c6424ae9d8de` | MasterChef rewards, admin wrapper, migrator |
| VVS Zap | `vvs-finance/vvs-zap` | `bb43b176b80b80af53e2d17de903cf5b5a4acd12` | Multi-leg zap slippage and residual handling |
| Ethena Code4Arena | `ethena-labs/code4arena-contest` | `7ffedb8873c2286930804e1c4feee0410fd0f033` | USDe contest snapshot corroboration |
| TON Liquid Staking | `ton-blockchain/liquid-staking-contract` | `1f4e9badbed52a4cf80cc58e4bb36ed375c6c8e7` | Payout NFTs, validator recovery, split authority |
| TON Nominator Pool | `ton-blockchain/nominator-pool` | `2f35c36b5ad662f10fd7b01ef780c3f1949c399d` | Withdrawal queue drain and stake gating |
| TON Whales Nominators | `tonwhales/ton-nominators` | `0553e1b6ddfc5c0b60505957505ce58d01bec3e7` | Nominator-pool corroboration |
| TON Vesting | `ton-blockchain/vesting-contract` | `2a63cb96942332abf92ed8425b37645fe4f41f86` | Locked custody and message-shape firewall |
| JitoSOL Wormhole Updater | `jito-foundation/jitosol-wormhole-updater` | `f5992a9c899072643613b1f2e3a53c02c2e0aadc` | Account-slice bridged exchange-rate relay |
| Ethena Code4rena | `code-423n4/2023-10-ethena` | `9fd8e26fc596601c3359ceac8951740c4d5e09c7` | Signed mint/redeem, custody route, hot-buffer risks |
| Velodrome V2 | `velodrome-finance/contracts` | `b3065d8b6702b14b094f9f6046b752cc9f78c43b` | Zaps, fee escrow, gauge rewards |

## Accepted Catalog Updates

- Added [Segregated AMM Fee Escrow](../../patterns/liquidity/pattern-segregated-amm-fee-escrow.md), [Round-Scoped Transferable Payout Receipts](../../patterns/vaults/pattern-round-scoped-transferable-payout-receipts.md), [Grace-Period Keeper Bounties](../../patterns/automation/pattern-grace-period-keeper-bounties.md), and [Vested Custody Capability Firewall](../../patterns/access-control/pattern-vested-custody-capability-firewall.md).
- Updated signed custody-routed mints to distinguish strict route-bound signatures from operator-selected custody routes that cannot change user economics.
- Updated delegated order signer, block-scoped mint/redeem throttle, custodial backing, balance-delta accounting, bridged source-rate relay, withdrawal buffer, async receipt, zap, lazy reward, gauge reward, epoch bucket, inflation, migrator, timelock, and anti-pattern guidance.
- Added anti-pattern guidance for duplicate staking asset registration, bitmap nonce domain truncation, timelock wrappers that only delay ownership handoff, and multi-leg zaps without per-leg slippage bounds.

## Rejected Or Deferred Candidates

- `vvs-finance/vvs-swap-core` and `vvs-finance/vvs-swap-periphery` are mostly Uniswap V2-style mechanics already covered by AMM, stateless router, minimum-liquidity, and balance-delta transfer docs.
- `ethena-labs/code4arena-contest` largely duplicates the USDe files in `code-423n4/2023-10-ethena`; it was counted as a source inspection and used as corroboration rather than as an independent candidate.
- `tonwhales/ton-nominators` corroborates pending deposit and withdrawal staging, but did not include open tests strong enough for a standalone catalog item.
- VVS fixed block-time emissions were added as a bounded-inflation caveat, not as a standalone pattern, because the reusable lesson is narrower than the farm implementation.
- Velodrome reward catch-up loops were merged into existing epoch-bucket and reward-DoS docs instead of creating a separate risk page.

## Contradictions And Caveats

- The previous signed custody-routed mint wording was too strong for Ethena evidence: the inspected Ethena order type does not bind `Route`. The catalog now treats route omission as a guarded variant, not the default secure shape.
- A per-block redeem cap denominated in burned stablecoins does not by itself cap collateral outflow when the collateral amount is independently signed.
- VVS Zap enforces a final output minimum, but its internal zero-minimum swap and liquidity legs still justify per-leg bounds in the zap guidance.
- A timelock wrapper does not provide timelocked governance if the sensitive economic setters are forwarded immediately.
