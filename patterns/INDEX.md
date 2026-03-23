# Pattern Library Index

> Auto-generated from pattern metadata. Regenerate: `python3 scripts/generate-pattern-index.py`

## oracles

### Patterns

| File | Description | Use When |
|------|-------------|----------|
| pattern-chainlink-integration.md | Integrate Chainlink price feeds for reliable off-chain oracle data with built-in manipulation resistance. | Need manipulation-resistant price for major assets; Asset has Chainlink feed available |
| pattern-dex-spot-price.md | Read current price directly from DEX pool — real-time but manipulation-vulnerable. | Need real-time price for display purposes; Combined with other validation (not used alone for value transfer) |
| pattern-historical-bounds.md | Validate price against historical min/max to detect anomalies and extreme deviations. | Need sanity check for oracle prices; Want to detect extreme price movements |
| pattern-multi-source-validation.md | Cross-check prices from multiple oracle sources to detect anomalies and identify which source is malfunctioning. | High-value operations depend on oracle price; Need to distinguish between oracle types of failures |
| pattern-multihop-price.md | Derive token price in USD through an intermediate base asset when no direct token/stable pool exists. | Token has no direct pool against stablecoins; Token has liquidity against major assets (WETH, WBTC) |
| pattern-twap-oracle.md | Time-Weighted Average Price from DEX pools — manipulation-resistant on-chain price discovery. | Need manipulation-resistant on-chain price; Asset has sufficient DEX liquidity |

### Risks

| File | Triggered When |
|------|---------------|
| risk-oracle-centralization.md | Relying on a single oracle source creates single points of failure and trust assumptions. |
| risk-oracle-frontrunning.md | Attackers exploit predictable oracle updates to front-run price changes and extract value. |
| risk-oracle-staleness.md | Using outdated price data leads to incorrect valuations and creates arbitrage opportunities. |
| risk-price-manipulation.md | Attackers manipulate on-chain price sources to exploit protocols that rely on them. |

### Requirements

| File | Applies To |
|------|-----------|
| req-oracle-reliability.md | R1: Freshness, R2: Accuracy, R3: Manipulation Resistance, R4: Availability |

## vaults

### Patterns

| File | Description | Use When |
|------|-------------|----------|
| pattern-async-deposit.md | Separate the request and execution of deposits/withdrawals to eliminate timing arbitrage opportunities. | Vault has significant oracle latency or deviation; Underlying assets are illiquid (RWA, staked assets) |
| pattern-circuit-breaker.md | Pause deposits/withdrawals when oracle price deviates significantly from a reference price, closing the attack window during suspicious conditions. | Vault relies on oracle for NAV calculation; Assets are volatile or oracle is known to have latency |
| pattern-clone-factory.md | Mass deployment of parameterized vault instances via minimal proxy clones — ~45K gas per vault instead of ~2M. | Many vaults with identical logic but different parameters (fee tiers, recipients, names) |
| pattern-delta-nav.md | Calculate vault shares based on proportional change in Net Asset Value. | Single-asset vault (one underlying token) |
| pattern-dynamic-premium.md | Entry/exit fee that varies based on oracle volatility, providing adaptive protection against oracle arbitrage during high-risk periods. | Vault has varying risk levels over time; Fixed premium would be too high during normal conditions |
| pattern-high-water-mark-fee.md | Charge performance fee only on new profit above the previous peak, paid via share dilution. | Vault generates yield and protocol needs to capture a share of profits |
| pattern-premium-buffer.md | Charge a fee on deposits/withdrawals that covers potential oracle price deviation, eliminating arbitrage profitability. | Vault uses oracle prices for NAV calculation; Need simple, synchronous deposit/withdraw flow |
| pattern-proportional-deposit.md | Users deposit and withdraw all vault assets proportionally, eliminating the need for oracle-based NAV calculation. | Multi-asset vault/pool with known composition; Want to avoid oracle dependency entirely |
| pattern-proportional-zapin.md | External periphery contract converts single-token input into a proportional multi-token deposit, pushing swap slippage to the depositor and eliminating slippage socialisation in managed vaults. | Multi-token vault where a manager rebalances after single-token deposits (slippage socialised across holders) |
| pattern-timelock-shares.md | Shares are issued immediately but cannot be transferred or redeemed for a specified period, preventing instant arbitrage profit extraction. | Want instant share issuance (better UX than async); Need to prevent flash loan attacks |
| pattern-vault-wrapper.md | Thin ERC4626 vault that wraps a base strategy vault, adding fee/access layers without duplicating strategy logic. | Multiple fee tiers needed over a single strategy (e.g. 0%, 10%, 15%) |

### Risks

| File | Triggered When |
|------|---------------|
| risk-oracle-arbitrage.md | NAV calculation using oracles creates arbitrage opportunities when oracle prices deviate from real market prices. |
| risk-vault-composability.md | Layered ERC4626 vaults introduce compound risks — rounding amplification, shared capacity, propagated failures — not present in single-vault architectures. |

### Requirements

| File | Applies To |
|------|-----------|
| req-vault-fairness.md | R1: No Value Extraction, R2: Fair Share Price, R3: Cost Attribution, R4: No Timing Advantage |
