# Batch 25 Findings

## Source Repositories

| Protocol | Repository | Commit | Focus |
|----------|------------|--------|-------|
| Balancer V3 | `balancer/balancer-v3-monorepo` | `0a5890a8c5d79865498d75cdc6ecdc75cf8d297d` | Vault accounting, hooks, buffers |
| Balancer V2 | `balancer/balancer-v2-monorepo` | `316ded078ddc2f1b28da5804d25752af67453435` | Vault registry and pool tokens |
| CoW Protocol | `cowprotocol/contracts` | `c6b61ce75841ce4c25ab126def9cc981c568e6c6` | Batch auction settlement |
| 1inch Limit Order Protocol | `1inch/limit-order-protocol` | `7da29889efa2e635611e1caf60f85f595ff7f05f` | Typed limit orders and invalidation |
| 1inch Solidity Utils | `1inch/solidity-utils` | `4adc76ed79fc5f2f0bd65a13cb6017788e1eb86d` | Permit and SafeERC20 helpers |
| 0x Protocol | `0xProject/protocol` | `b319a4dceb5053a4794bf53dbeeaeb416c31ef0a` | Native orders and RFQ |
| Trader Joe V2 | `traderjoe-xyz/joe-v2` | `067c6ccf5b8ff1526d03fa3e4c65ec45d01c1f73` | Liquidity Book AMM |
| SushiSwap | `sushi-labs/sushiswap` | `7b37fbee46327dc18f8a0866ab7d0b83751597e5` | SDK/generated bindings review |
| Synthetix V3 | `synthetixio/synthetix-v3` | `23585f73c76d625b2a43aaf94dc440a8a1e7a8fa` | Core debt, perps, oracle manager |
| Gearbox Core V3 | `gearbox-protocol/core-v3` | `b038597d9070d9fd18593a6ae9c3d28ca931bb73` | Credit accounts and quotas |
| Ajna Core | `ajna-finance/ajna-core` | `0f59e78031af76d62ad575c18405eb325b28849f` | Price-bucket lending |
| Angle Transmuter | `angleprotocol/angle-transmuter` | `2fa74b73a3f5aa921e619e55744d73228cd2fe71` | Collateral-ratio redemptions |
| Abracadabra MIM | `abracadabra-money/magic-internet-money` | `23266d17969a95e69199670cba9d0060bff33340` | Cauldron and whitelisting |

`traderjoe-xyz/joe-v2.1`, `Synthetixio/synthetix`, and
`origin-dollar/origin-dollar` were unavailable or private during this batch and
are not counted.

## Accepted Catalog Updates

- Added [Oracle-Free Price-Bucket Lending Book](../../patterns/lending/pattern-oracle-free-price-bucket-lending-book.md) and [Collateral-Ratio Pro-Rata Redemption](../../patterns/token-integration/pattern-collateral-ratio-pro-rata-redemption.md).
- Updated AMM factory, singleton settlement, hook permissions, hook-adjusted accounting, dynamic hook fees, vault-wrapper, exchange-rate valuation, discrete-bin liquidity, volatility-fee, and router docs with Balancer and Trader Joe evidence.
- Updated signed-order settlement and anti-pattern guidance with CoW, 1inch, and 0x evidence for balance lanes, extension hashes, invalidation ledgers, RFQ `tx.origin` caveats, permit front-run tolerance, and callback trust boundaries.
- Updated lending docs with Gearbox credit-account frames, Ajna bucket lending and bonded auctions, explicit bad-debt waterfalls, multi-component debt repayment, hard utilization stops, proof-capped resulting debt, and stale-price liquidation caveats.
- Updated Synthetix V3 perps, debt-distribution, oracle node-graph, collateral-haircut, and debt-bearing migration guidance.
- Updated Angle Transmuter oracle and redemption guidance for action-scoped stable-asset bounds, global collateral-ratio penalties, and pro-rata reserve claims.

## Rejected Or Deferred Candidates

- Balancer invariant math, minimum BPT supply, generic ERC4626 wrapping, and generic pause/deadline/min-output behavior were duplicates of existing invariant, minimum-liquidity, vault-wrapper, and slippage guidance.
- Angle caps and fee curves were treated as corroboration for existing reserve-cap and dynamic-fee docs rather than new patterns.
- EIP-712 basics, ERC-1271 basics, delegated signers, zero-amount checks, taker threshold checks, and 0x bridge balance-delta accounting duplicated existing signature, slippage, and token-integration guidance.
- Trader Joe V1 constant-product mechanics duplicated existing AMM invariant docs.
- SushiSwap material in this batch was mostly SDK or generated bindings, so it was not used as primary protocol evidence.
- Synthetix ERC4626 and wstETH wrapper timestamp notes duplicated existing wrapper and oracle timestamp cautions.
- Gearbox threshold ramp behavior, DegenBox rebase share conversion, and generic Chainlink `latestAnswer` wrapper issues duplicated existing ramp, share-accounting, and oracle anti-pattern guidance.

## Contradictions And Caveats

- "One canonical pool per token pair" is not universal. Balancer V3 and Trader Joe V2 show that canonical identity may include hooks, rate providers, token configuration, bin step, version, or other immutable parameters.
- Balancer BPT or rate-scaled balances are accounting inputs for pool math and fee accounting, not proof of market-clearing LP value or LP virtual-price monotonicity.
- `tx.origin` remains an anti-pattern as a security or entitlement boundary. The only accepted caveat is maker-chosen RFQ origin filtering inside a signed order with independent maker, taker, expiry, fill-state, and registry checks.
- Abracadabra `cook` exchange-rate guard naming is easy to misread: the inspected V3 contracts name the argument `maxRate` while requiring the updated rate to be greater than it in `/private/tmp/defillama-source/abracadabra-money__magic-internet-money/contracts/CauldronV3.sol:455-458` and sibling variants. The catalog records this as a stale-price policy caveat, not a naming pattern.
- Oracle-free bucket lending removes a protocol oracle from borrow sizing, but lenders still underwrite price risk through bucket placement, liquidation settlement, and bucket bankruptcy behavior.
