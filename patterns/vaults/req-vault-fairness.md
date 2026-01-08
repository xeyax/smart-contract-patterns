# Vault Fairness Requirements

> Core requirements that vault deposit/withdraw mechanisms must satisfy.

## Overview

These requirements define what "fair" means for vault operations. Patterns and risks in this category should reference these requirements to verify correctness.

---

## R1: No Value Extraction

**Entering or exiting users must not be able to extract value at the expense of existing shareholders.**

```
After deposit:  value(existing_shares) >= value_before(existing_shares)
After withdraw: value(remaining_shares) >= value_before(remaining_shares)
```

### What This Means
- Depositor's gain should come only from their own contribution
- Withdrawer's payout should come only from their own share
- No "free money" from timing, information asymmetry, or calculation errors

### Violations
- [Oracle Arbitrage](./risk-oracle-arbitrage.md) — stale prices allow value extraction

---

## R2: Fair Share Price

**User receives shares proportional to the real value of deposited assets.**

```
shares_received     real_value_deposited
────────────────  = ────────────────────
total_shares_after    real_nav_after
```

### What This Means
- If user deposits 10% of vault's real value, they should get 10% of shares
- "Real value" = actual market value, not stale oracle value
- No systematic over/under pricing of shares

### Violations
- deltaNav calculated with stale oracle ≠ real deposited value
- Atomic swap at price different from NAV calculation price

---

## R3: Cost Attribution

**Operational costs are paid by the user who initiates them.**

```
If deposit requires swap:       slippage_cost paid by depositor
If withdraw requires liquidation: liquidation_cost paid by withdrawer
```

### What This Means
- Rebalancing costs don't fall on existing shareholders
- Each user pays for their own "onboarding" or "exit" costs
- Protocol operations (keeper calls, rebalancing) may be socialized if they benefit all

### Violations
- Atomic swap slippage absorbed by vault (paid by all shareholders)
- Liquidation costs spread across remaining holders

### Solutions
- [Premium Buffer](./pattern-premium-buffer.md) — fee covers expected costs
- [Async Deposit](./pattern-async-deposit.md) — costs handled separately from share minting

---

## R4: No Timing Advantage

**User cannot exploit advance knowledge of NAV changes.**

```
Information available at time T should not enable
risk-free profit from deposit/withdraw at time T
```

### What This Means
- Knowing that NAV will increase shouldn't enable profitable deposit
- Knowing that NAV will decrease shouldn't enable profitable withdraw
- No front-running vault operations

### Violations
- Predictable oracle updates
- Pending harvests visible in mempool
- Known rebalancing schedules

### Solutions
- [Async Deposit](./pattern-async-deposit.md) — delayed settlement removes timing advantage
- Profit locking (Yearn-style) — profits unlock gradually

---

## Verification Checklist

When evaluating a vault pattern, verify:

| Requirement | Question to Ask |
|-------------|-----------------|
| R1 | Can any user action decrease value of other users' shares? |
| R2 | Is share price based on real (not stale) asset values? |
| R3 | Who pays for swaps, liquidations, rebalancing? |
| R4 | Can timing of deposit/withdraw be exploited? |

---

## Related Documents

### Patterns (Solutions)
- [Delta NAV Share Accounting](./pattern-delta-nav.md) — base accounting method
- [Premium Buffer](./pattern-premium-buffer.md) — satisfies R1, R3 via fees
- [Async Deposit/Withdrawal](./pattern-async-deposit.md) — satisfies R4
- [Proportional Deposit/Withdrawal](./pattern-proportional-deposit.md) — satisfies R1, R2 without oracles

### Risks (Violations)
- [Oracle Arbitrage Risk](./risk-oracle-arbitrage.md) — violates R1, R2, R4
