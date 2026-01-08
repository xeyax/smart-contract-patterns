# Oracle Arbitrage Risk

> NAV calculation using oracles creates arbitrage opportunities when oracle prices deviate from real market prices.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, oracle, arbitrage, nav, risk, mev |
| Type | Risk Description |

## Problem Description

When a vault calculates NAV using oracle prices (Chainlink, TWAP, etc.), there's inherent latency between:
- **Oracle price** — what the vault uses for share calculation
- **Market price** — what assets actually trade for on DEXes

This discrepancy creates risk-free arbitrage opportunities at the expense of existing shareholders.

## Requirements Violated

This risk violates [Vault Fairness Requirements](./req-vault-fairness.md):
- **R1: No Value Extraction** — attacker extracts value from existing shareholders
- **R2: Fair Share Price** — shares priced on stale oracle, not real value
- **R3: Cost Attribution** — in some variants, swap/rebalance costs are socialized
- **R4: No Timing Advantage** — attacker exploits knowledge of price discrepancy

## Attack Vectors

### Key Insight: When Does Oracle "Cancel Out"?

```
shares = deltaNav × totalShares / navBefore
```

If `deltaNav` and `navBefore` are both calculated using the **same oracle prices**, errors cancel out. If they use **different price sources**, arbitrage is possible.

---

### 1. Single-Asset Vault: No Swap (ARBITRAGE)

Deposit stays as different asset (e.g., USDC into ETH vault):

```
Vault: 5 ETH
Oracle: ETH = $1800 (stale LOW)
Market: ETH = $2000 (real)
totalShares = 100

navBefore = 5 × $1800 = $9,000 (understated)
Real value = 5 × $2000 = $10,000

User deposits 1000 USDC (no swap)
navAfter = $9,000 + $1,000 = $10,000
deltaNav = $1,000 (correct, USDC doesn't use oracle)

shares = 1000 × 100 / 9000 = 11.11 shares
User ownership: 11.11 / 111.11 = 10%

Real value after = $10,000 + $1,000 = $11,000
User's real value = 10% × $11,000 = $1,100
Existing real value = 90% × $11,000 = $9,900
```

**User paid $1000, got $1,100 → PROFIT $100**
**Existing had $10,000, now $9,900 → LOSS $100**

**Violates R1, R4:** deltaNav (USDC) doesn't depend on oracle, but navBefore does.

---

### 2. Single-Asset Vault: With Swap (NO ARBITRAGE)

Deposit converted to vault asset:

```
Vault: 5 ETH
Oracle: ETH = $1800 (stale LOW)
Market: ETH = $2000 (real)
totalShares = 100

navBefore = 5 × $1800 = $9,000

User deposits 1000 USDC → swap → 0.5 ETH (at market)
navAfter = 5.5 × $1800 = $9,900
deltaNav = $900 (oracle-based, same as navBefore)

shares = 900 × 100 / 9000 = 10 shares
User ownership: 10 / 110 = 9.09%

Real value after = 5.5 × $2000 = $11,000
User's real value = 9.09% × $11,000 = $1,000
```

**User paid $1000, got $1,000 → FAIR**

Oracle errors in deltaNav and navBefore **cancel out** because both use ETH oracle.

---

### 3. Multi-Asset Vault: With Swap (ARBITRAGE)

Even with swap, other assets with stale oracle create arbitrage:

```
Vault: 5 ETH + 1 WBTC
ETH oracle: $2000 (correct)
WBTC oracle: $40,000 (stale LOW, real = $42,000)
totalShares = 100

navBefore = 5×$2000 + 1×$40,000 = $50,000 (understated)
Real value = 5×$2000 + 1×$42,000 = $52,000

User deposits 1000 USDC → swap → 0.5 ETH
navAfter = 5.5×$2000 + 1×$40,000 = $51,000
deltaNav = $1,000

shares = 1000 × 100 / 50,000 = 2 shares
User ownership: 2 / 102 = 1.96%

Real value after = 5.5×$2000 + 1×$42,000 = $53,000
User's real value = 1.96% × $53,000 = $1,039
```

**User paid $1000, got $1,039 → PROFIT $39**

**Violates R1:** WBTC stale oracle affects navBefore, but swap was in ETH (correct oracle). Errors don't cancel.

---

### 4. Withdraw with Asset Conversion (ARBITRAGE)

If withdrawal converts to different asset using oracle price:

```
Vault: 5 ETH
Oracle: $2100 (stale HIGH)
Market: $2000 (real)

User has 10 shares (10%)
Vault calculates: 10% × 5 ETH × $2100 = $1,050 worth
User requests withdrawal in USDC
Vault sells 0.525 ETH at market → $1,050 USDC

But real value of 10% = 0.5 ETH = $1,000
User extracts $50 extra
```

**Violates R1:** Oracle used for conversion calculation differs from market execution.

---

### 5. In-Kind Withdrawal (NO ARBITRAGE)

If user receives the vault asset directly, no oracle conversion needed:

```
Vault: 5 ETH
Oracle: $2100 (stale HIGH)
Market: $2000 (real)

User has 10 shares (10%)
User withdraws in-kind → receives 0.5 ETH

Real value = 0.5 × $2000 = $1,000
User paid $1,000 originally → FAIR
```

Oracle price is irrelevant — user gets proportional slice of actual assets.

Same logic applies to multi-asset vaults with proportional (all-asset) withdrawal.

---

### 6. Multi-Asset Single-Asset Withdrawal (ARBITRAGE)

User withdraws single asset from multi-asset vault:

```
Vault: 5 ETH + 1 WBTC
ETH oracle: $2000 (correct)
WBTC oracle: $42,000 (stale HIGH, real = $40,000)
totalShares = 100

navBefore = 5×$2000 + 1×$42,000 = $52,000 (overstated)
Real value = 5×$2000 + 1×$40,000 = $50,000

User has 10 shares (10%)
Share value per oracle: 10% × $52,000 = $5,200
User requests withdrawal in ETH only
Vault gives: $5,200 / $2000 = 2.6 ETH

Real value received = 2.6 × $2000 = $5,200
But fair share of real vault = 10% × $50,000 = $5,000
User extracts $200 extra
```

**Violates R1, R4:** Overstated WBTC oracle inflates share value; user exits in correctly-priced ETH.

---

## Deposit Summary Table

| Vault Type | Deposit | Oracle Stale For | Arbitrage? |
|------------|---------|------------------|------------|
| Single-asset | No swap | Vault asset | **YES** |
| Single-asset | Swap to vault asset | Vault asset | No (cancels) |
| Multi-asset | Swap to any asset | Any other asset | **YES** |
| Multi-asset | No swap | Any asset | **YES** |

## Withdrawal Summary Table

| Vault Type | Withdrawal | Oracle Stale For | Arbitrage? |
|------------|------------|------------------|------------|
| Single-asset | In-kind (receive vault asset) | Any | No |
| Single-asset | Convert to other asset | Vault asset | **YES** |
| Multi-asset | In-kind (receive all assets) | Any | No |
| Multi-asset | Single-asset out | Any asset | **YES** |

## Conditions That Increase Risk

| Factor | Higher Risk | Lower Risk |
|--------|-------------|------------|
| Oracle update frequency | Low (hourly) | High (every block) |
| Oracle deviation threshold | High (1-2%) | Low (0.1%) |
| Asset volatility | High (memecoins) | Low (stablecoins) |
| Vault TVL | Low | High |
| Deposit/withdraw size | Large relative to TVL | Small |

## Impact Calculation

Potential arbitrage profit per operation:

```
profit = deposit_amount × oracle_deviation_percentage
```

Example with 1% oracle deviation threshold:
- $100,000 deposit → up to $1,000 arbitrage profit
- Profit comes directly from other shareholders

## Why This Matters

1. **Permanent loss** — unlike AMM arbitrage, vault arbitrage extracts value that cannot be recovered
2. **Compounds over time** — each arbitrage event dilutes existing shareholders
3. **Attracts MEV bots** — automated extraction becomes profitable
4. **Erodes trust** — sophisticated actors profit at expense of retail users

## Mitigations

| Pattern | How It Helps | Trade-off |
|---------|--------------|-----------|
| [Premium Buffer](./pattern-premium-buffer.md) | Fee covers oracle deviation | Worse UX, cost to users |
| [Async Deposit/Withdrawal](./pattern-async-deposit.md) | Eliminates timing advantage | Delayed settlement |
| [Proportional Deposit/Withdrawal](./pattern-proportional-deposit.md) | No oracle needed | User must have all assets |

## Related Patterns

- [Delta NAV Share Accounting](./pattern-delta-nav.md) — base pattern that has this risk
- [Premium Buffer](./pattern-premium-buffer.md) — mitigation via fees
- [Async Deposit/Withdrawal](./pattern-async-deposit.md) — mitigation via delayed settlement

## References

- [Oracle Manipulation in ERC4626](https://github.com/code-423n4/2024-04-renzo-findings/issues/424)
- [Euler Finance: Exchange Rate Manipulation](https://www.euler.finance/blog/exchange-rate-manipulation-in-erc4626-vaults)
- [Chainlink Deviation Thresholds](https://docs.chain.link/data-feeds)
