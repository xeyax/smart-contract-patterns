# Pattern Library Index

> Auto-generated from pattern metadata. Regenerate: `python3 scripts/generate-pattern-index.py`

## access-control

### Patterns

| File | Description | Use When |
|------|-------------|----------|
| pattern-bootstrap-authority-handoff.md | Let a factory hold temporary setup authority only long enough to wire a contract graph, then transfer all lasting roles to the intended owner. | A factory deploys multiple contracts that must be configured atomically |
| pattern-break-glass-risk-limiter.md | Give an emergency role narrowly scoped powers to reduce risk limits or disable risky routes without granting the power to re-enable them. | Operators need to react faster than governance during suspected compromise or market stress |
| pattern-consumer-scoped-rate-limiter.md | Apply token-bucket limits per approved consumer or route so one actor cannot exhaust shared capacity for unrelated flows. | Multiple protocol components share a constrained operation such as instant redemption, bridge egress, or privileged cons |
| pattern-mutual-parameter-acceptance.md | Require both affected parties to accept shared economic parameters before the new values take effect. | A parameter affects two independent parties, such as manager and user, partner and protocol, or splitter recipients |
| pattern-participant-permission-bitmap.md | Encode participant eligibility as compact policy bits so deposits, borrows, transfers, and exits can enforce both account-level and pool-level access. | A pool has private, public, pool-level, or function-level participation modes |
| pattern-selector-scoped-authority.md | Grant operators permission to call specific function selectors on specific targets instead of granting broad owner or admin authority. | Operators need to run recurring maintenance or risk-management calls |
| pattern-two-step-authority-handoff.md | Stage critical authority or withdrawal-address changes and require confirmation by the new address before activation. | A privileged role controls upgrades, pausing, treasury movement, or withdrawal addresses |

## cross-chain

### Patterns

| File | Description | Use When |
|------|-------------|----------|
| pattern-chain-bound-request-hash.md | Bind cross-chain requests to source chain, destination chain, nonce, operation, participants, value, and payload before accepting remote confirmation. | A bridge mints, burns, unlocks, or confirms value on another chain |
| pattern-custodian-attested-mint-burn.md | Mint and burn wrapped assets through merchant requests that are approved and reconciled by a trusted custodian. | The source asset is not trustlessly verifiable on the destination chain |
| pattern-deterministic-cross-chain-factory.md | Deploy peer contract systems at predictable addresses across chains so cross-chain configuration can be precomputed and verified. | The same protocol graph is deployed on multiple chains |
| pattern-signed-custody-routed-mint.md | Authorize mint and redeem orders with typed signatures that bind route, custodian allocation, nonce, expiry, and asset ratios before custody-backed settlement. | Tokens are minted or redeemed against off-chain or custodied reserves |

### Requirements

| File | Applies To |
|------|-----------|
| req-custodial-reserve-backing.md | R1: Full Backing, R2: Public Verifiability, R3: Settlement Traceability, R4: Operational Liveness |

## governance

### Patterns

| File | Description | Use When |
|------|-------------|----------|
| pattern-bounded-token-inflation.md | Constrain privileged token minting with explicit rate, amount, recipient, and delay bounds so governance cannot silently create unlimited supply. | Governance or a rewards controller can mint protocol tokens; Inflation is expected but should be predictable |

## lending

### Patterns

| File | Description | Use When |
|------|-------------|----------|
| pattern-bounded-rate-source-adapter.md | Convert an external benchmark or savings rate into a lending rate only after applying freshness, bounds, spread, and fallback rules. | Borrow or supply rates should follow an external benchmark |
| pattern-comptroller-risk-gate.md | Route market actions through a central risk module that approves borrows, redeems, transfers, and liquidations before state changes. | A lending protocol has multiple collateral and borrow markets |
| pattern-explicit-bad-debt-realization.md | When liquidation cannot cover debt, reduce market supply and borrow totals immediately so insolvency is visible instead of hidden in stale accounting. | Liquidation can leave debt uncovered after seizing all collateral |
| pattern-isolated-permissionless-market.md | Let anyone create lending markets only when each market's collateral, debt, oracle, and interest-rate state is isolated from every other market. | The protocol wants permissionless market creation |
| pattern-kinked-utilization-rate-model.md | Increase borrow rates slowly below a target utilization and sharply above it to discourage liquidity exhaustion. | A lending market needs dynamic borrow and supply rates |
| pattern-lazy-borrow-index.md | Track global borrow interest with an index so borrower debt can be updated on demand instead of looping over all borrowers. | Borrow interest accrues continuously or per block; The protocol has many borrowers |
| pattern-reserve-exposure-caps.md | Bound how much a lending market can supply, borrow, or expose to one asset so risk parameters cannot rely on liquidation mechanics alone. | A market lists assets with limited liquidity or correlated risk |
| pattern-scaled-balance-token-accounting.md | Store token balances scaled by a liquidity or debt index so interest accrues globally while user balances update lazily. | A lending protocol represents supplied or borrowed positions as transferable or account-bound tokens |
| pattern-share-denominated-lending-accounting.md | Track supply and borrow positions as market shares against total assets so interest and losses are allocated proportionally. | A lending market needs proportional supply or borrow accounting |

### Requirements

| File | Applies To |
|------|-----------|
| req-credit-loss-accounting.md | R1: Loss State Is Explicit, R2: Losses Cannot Exceed Accounted Assets, R3: Normal Issuance Respects Loss State |
| req-lending-accounting-freshness.md | R1: Accrue Before Value-Changing Actions, R2: Freshness Scope Is Explicit, R3: Stale Actions Fail Closed |

## monitoring

### Patterns

| File | Description | Use When |
|------|-------------|----------|
| pattern-read-only-protocol-health-checker.md | Package production and fork invariant checks into read-only contracts or scripts that return structured health results without mutating protocol state. | A protocol has many deployed pools, strategies, managers, or upgradeable instances |

## oracles

### Patterns

| File | Description | Use When |
|------|-------------|----------|
| pattern-chainlink-integration.md | Integrate Chainlink price feeds for reliable off-chain oracle data with built-in manipulation resistance. | Need manipulation-resistant price for major assets; Asset has Chainlink feed available |
| pattern-dex-spot-price.md | Read current price directly from DEX pool — real-time but manipulation-vulnerable. | Need real-time price for display purposes; Combined with other validation (not used alone for value transfer) |
| pattern-historical-bounds.md | Validate price against historical min/max to detect anomalies and extreme deviations. | Need sanity check for oracle prices; Want to detect extreme price movements |
| pattern-multi-source-validation.md | Cross-check prices from multiple oracle sources to detect anomalies and identify which source is malfunctioning. | High-value operations depend on oracle price; Need to distinguish between oracle types of failures |
| pattern-multihop-price.md | Derive token price in USD through an intermediate base asset when no direct token/stable pool exists. | Token has no direct pool against stablecoins; Token has liquidity against major assets (WETH, WBTC) |
| pattern-peg-ratio-monitor.md | Track normalized market-price and fair-value ratios for pegged or redeemable assets so operators can detect depeg before it becomes bad debt. | An asset should trade near a peg, redemption value, or exchange-rate value |
| pattern-threshold-reporter-consensus.md | Require a quorum of permissioned reporters to submit the same oracle payload before mutating accepted protocol state. | A protocol has a trusted reporter set for off-chain observations |
| pattern-twap-oracle.md | Time-Weighted Average Price from DEX pools — manipulation-resistant on-chain price discovery. | Need manipulation-resistant on-chain price; Asset has sufficient DEX liquidity |

### Risks

| File | Triggered When |
|------|---------------|
| risk-exchange-rate-valuation.md | Collateral value comes from staking, vault, or wrapper exchange rates |
| risk-oracle-centralization.md | Relying on a single oracle source creates single points of failure and trust assumptions. |
| risk-oracle-frontrunning.md | Attackers exploit predictable oracle updates to front-run price changes and extract value. |
| risk-oracle-staleness.md | Using outdated price data leads to incorrect valuations and creates arbitrage opportunities. |
| risk-price-manipulation.md | Attackers manipulate on-chain price sources to exploit protocols that rely on them. |

### Requirements

| File | Applies To |
|------|-----------|
| req-oracle-reliability.md | R1: Freshness, R2: Accuracy, R3: Manipulation Resistance, R4: Availability |

## rewards

### Patterns

| File | Description | Use When |
|------|-------------|----------|
| pattern-delayed-cumulative-merkle-claims.md | Stage Merkle reward roots behind a delay and let users claim only the cumulative delta above what they have already received. | Rewards are computed off-chain and published periodically |
| pattern-lazy-reward-index.md | Accrue rewards through a global index and update each user only when they interact or claim. | Rewards accrue continuously or per emission update; The protocol has many suppliers, stakers, or borrowers |
| pattern-queued-reward-streaming.md | Queue reward tokens from permissioned distributors, carry leftovers forward, and stream rewards over a fixed duration. | Rewards arrive in discrete deposits but should accrue smoothly; Only approved distributors should fund reward streams |

## token-integration

### Patterns

| File | Description | Use When |
|------|-------------|----------|
| pattern-balance-delta-transfer-accounting.md | Account for the actual token amount received by measuring balance changes around transfers. | The protocol accepts arbitrary or curated ERC20 collateral |

## upgrades

### Patterns

| File | Description | Use When |
|------|-------------|----------|
| pattern-namespaced-storage-accessor.md | Isolate upgradeable contract state behind explicit namespace slots and typed accessor libraries. | Contracts are upgradeable and use inheritance or libraries; Multiple modules need independent storage layouts |
| pattern-version-gated-upgrade-registry.md | Authorize proxy upgrades only to implementation versions that a registry has approved and not deprecated. | Many proxy instances should share a vetted implementation catalog |

## vaults

### Patterns

| File | Description | Use When |
|------|-------------|----------|
| pattern-async-deposit.md | Separate the request and execution of deposits/withdrawals to eliminate timing arbitrage opportunities. | Vault has significant oracle latency or deviation; Underlying assets are illiquid (RWA, staked assets) |
| pattern-bounded-rebalance-auction.md | Let managers rebalance basket vaults through auctions while constraining assets, weights, prices, duration, and later parameter changes. | A vault holds a managed basket or index of multiple assets |
| pattern-circuit-breaker.md | Pause deposits/withdrawals when oracle price deviates significantly from a reference price, closing the attack window during suspicious conditions. | Vault relies on oracle for NAV calculation; Assets are volatile or oracle is known to have latency |
| pattern-clone-factory.md | Mass deployment of parameterized vault instances via minimal proxy clones — ~45K gas per vault instead of ~2M. | Many vaults with identical logic but different parameters (fee tiers, recipients, names) |
| pattern-delta-nav.md | Calculate vault shares based on proportional change in Net Asset Value. | Single-asset vault (one underlying token) |
| pattern-dynamic-premium.md | Entry/exit fee that varies based on oracle volatility, providing adaptive protection against oracle arbitrage during high-risk periods. | Vault has varying risk levels over time; Fixed premium would be too high during normal conditions |
| pattern-high-water-mark-fee.md | Charge performance fee only on new profit above the previous peak, paid via share dilution. | Vault generates yield and protocol needs to capture a share of profits |
| pattern-locked-profit-smoothing.md | Exclude newly harvested profit from strategy value for a fixed window, then release it linearly to prevent timing extraction around harvests. | Strategy profit is realized in discrete harvest transactions; Deposits can occur immediately before or after harvest |
| pattern-premium-buffer.md | Charge a fee on deposits/withdrawals that covers potential oracle price deviation, eliminating arbitrage profitability. | Vault uses oracle prices for NAV calculation; Need simple, synchronous deposit/withdraw flow |
| pattern-proportional-deposit.md | Users deposit and withdraw all vault assets proportionally, eliminating the need for oracle-based NAV calculation. | Multi-asset vault/pool with known composition; Want to avoid oracle dependency entirely |
| pattern-proportional-zapin.md | External periphery contract converts single-token input into a proportional multi-token deposit, pushing swap slippage to the depositor and eliminating slippage socialisation in managed vaults. | Multi-token vault where a manager rebalances after single-token deposits (slippage socialised across holders) |
| pattern-timelock-shares.md | Shares are issued immediately but cannot be transferred or redeemed for a specified period, preventing instant arbitrage profit extraction. | Want instant share issuance (better UX than async); Need to prevent flash loan attacks |
| pattern-user-owned-proxy-vault.md | Deploy one vault/proxy per user so protocol integrations can be automated while custody and position ownership remain isolated. | Users need individualized positions in an external protocol |
| pattern-vault-wrapper.md | Thin ERC4626 vault that wraps a base strategy vault, adding fee/access layers without duplicating strategy logic. | Multiple fee tiers needed over a single strategy (e.g. 0%, 10%, 15%) |
| pattern-virtual-share-offset.md | Add virtual assets and virtual shares to vault conversion math so first-depositor donations cannot round later depositors to zero shares. | Vault share minting uses `assets * totalSupply / totalAssets` |
| pattern-withdrawal-liquidity-buffer.md | Reserve enough liquid assets for claims, route new inflows to queued withdrawal deficits first, and only deploy surplus capital. | Vault assets are deployed into illiquid, staked, or externally managed positions |

### Risks

| File | Triggered When |
|------|---------------|
| risk-oracle-arbitrage.md | NAV calculation using oracles creates arbitrage opportunities when oracle prices deviate from real market prices. |
| risk-vault-composability.md | Layered ERC4626 vaults introduce compound risks — rounding amplification, shared capacity, propagated failures — not present in single-vault architectures. |

### Requirements

| File | Applies To |
|------|-----------|
| req-vault-fairness.md | R1: No Value Extraction, R2: Fair Share Price, R3: Cost Attribution, R4: No Timing Advantage |
