# Vault Composability Risk

> Layered ERC4626 vaults introduce compound risks — rounding amplification, shared capacity, propagated failures — not present in single-vault architectures.

## Metadata

| Property | Value |
|----------|-------|
| Type | Risk Description |
| Category | vaults |
| Tags | ERC4626, composability, wrapper, meta-vault |

## Problem Description

When a [Wrapper Vault](./pattern-vault-wrapper.md) deposits into a Base Vault, two ERC4626 contracts interact on every operation. Each layer has its own rounding, access control, capacity limits, and failure modes. These interact in non-obvious ways, creating risks that don't exist in a standalone vault.

## Requirements Affected

- **R1 (No Value Extraction):** Double rounding can extract more value from small depositors than a single vault.
- **R3 (Cost Attribution):** Fee accrual ordering across layers can misattribute costs — wrapper fee dilution affects wrapper holders, not base vault holders.

## Risk Vectors

### 1. Double Rounding

Each ERC4626 vault rounds in its own favor: mint rounds down (fewer shares), redeem rounds down (fewer assets). With two layers, rounding compounds.

**Single vault:**
```
deposit 1000 USDT → 999 shares (1 wei rounding loss)
```

**Wrapper + base vault:**
```
deposit 1000 USDT → base vault: 999 base shares (1 wei loss)
                  → wrapper converts 999 base shares to value
                  → wrapper: 998 wrapper shares (1 more wei loss)
```

**Impact:** ~2 wei per operation. Negligible for normal amounts. Problematic only for dust deposits — an attacker depositing 1 wei repeatedly could grief gas without contributing value.

**Mitigation:** Set minimum deposit threshold in wrapper (`DepositTooSmall` revert for amounts below threshold).

### 2. Capacity Contention

All wrappers share the base vault's `maxTotalAssets`. No wrapper has guaranteed capacity.

```
Base vault cap: 1M USDT

Wrapper A deposits 600K ──► Base vault: 600K / 1M used
Wrapper B deposits 500K ──► REVERTS (only 400K remaining)
```

**Impact:** First-come-first-served race. A large deposit through one wrapper can block all other wrappers. During high demand, wrappers compete for limited capacity.

**Mitigation options:**

| Approach | Trade-off |
|----------|-----------|
| No limit — let wrappers compete | Simple, but unpredictable for partners |
| Per-wrapper quota in base vault | Fair, but adds complexity and storage |
| Dynamic cap based on wrapper count | Flexible, but requires governance |
| Large base vault cap | Avoids issue, but increases strategy risk |

### 3. Pause Propagation

When base vault is paused, all wrappers are effectively frozen — `deposit()` and `redeem()` revert on the base vault call.

```
Base vault PAUSED
    │
    ├── Wrapper A: deposit() → base.deposit() → REVERT
    ├── Wrapper B: redeem() → base.redeem() → REVERT
    └── Wrapper C: maxDeposit() should return 0
```

**Impact:** Wrapper users see confusing reverts if wrapper doesn't handle this gracefully.

**Mitigation:** Wrapper's `maxDeposit()` and `maxRedeem()` should delegate to base vault:

```solidity
function maxDeposit(address receiver) public view override returns (uint256) {
    return baseVault.maxDeposit(address(this));
}
```

This returns 0 when base is paused, giving UIs a clean signal.

### 4. Fee Accrual Ordering

Wrapper MUST accrue performance fee before every deposit and redeem. If skipped:

**Deposit without fee accrual:**
```
State: wrapper has 1000 shares, base PPS grew 10% (fee pending)
User deposits 1000 USDT → gets shares at current (pre-fee) PPS
Fee accrues later → dilutes ALL holders including new depositor
Result: new depositor pays part of fee they didn't owe
         fee recipient gets less than earned
```

**Redeem without fee accrual:**
```
State: wrapper has 1000 shares, base PPS grew 10% (fee pending)
User redeems 500 shares → exits at pre-fee PPS (higher value)
Fee accrues later → remaining 500 shares bear full fee
Result: exiting user avoids fee
         remaining holders subsidize
```

**Impact:** Systematic value transfer. Violates R1 (no value extraction) and R3 (cost attribution).

**Mitigation:** Call `_accruePerformanceFee()` as the first operation in both `_deposit()` and `_withdraw()`. See [HWM Fee Pattern](./pattern-high-water-mark-fee.md) for correct implementation.

### 5. Preview vs Actual Divergence

ERC4626 spec explicitly allows `previewDeposit()` to return a different value than actual `deposit()`. When wrapper chains two ERC4626 calls, divergence compounds:

```
Wrapper.previewDeposit(1000):
    baseShares_est = baseVault.previewDeposit(1000)  // estimate
    wrapperShares_est = f(baseShares_est)             // estimate of estimate

Wrapper.deposit(1000):
    baseShares_actual = baseVault.deposit(1000)       // may differ from preview
    wrapperShares_actual = f(baseShares_actual)        // different from estimate
```

**Impact:** Frontends showing `previewDeposit` may promise more shares than user actually receives. Slippage-sensitive integrations (aggregators, automated strategies) may revert on unexpected output.

**Mitigation:** Wrapper should not guarantee exact preview match. Frontends should add slippage tolerance. Alternatively, wrapper can calculate shares from actual base deposit result rather than from preview.

### 6. Base Vault Upgrade

If base vault is UUPS-upgradeable, an upgrade can change behavior without wrapper's knowledge:

```
Before upgrade:
    base.convertToAssets(1e18) = 1.05e6 (USDT, 6 decimals)

After upgrade (new rounding, new fee, new NAV calc):
    base.convertToAssets(1e18) = 1.04e6

Wrapper's HWM: 1.05e18 (set before upgrade)
Result: basePPS < HWM → no fee accrual (correct)
        but wrapper's totalAssets() decreased → share price dropped
        users lost value through no fault of their own
```

**Impact:** Silent change in wrapper economics. Could cause HWM to become unreachable if base vault's PPS formula changed.

**Mitigation:** Monitor base vault upgrade events. Consider a circuit breaker in wrapper that pauses on unexpected PPS drops. Document base vault upgrade policy for wrapper deployers.

### 7. Sandwich Amplification

Sandwich attacks on a wrapper have two entry points:

```
Standard sandwich (single vault):
    Attacker deposits → Victim deposits → Attacker redeems
    Profit: oracle_error × victim_amount

Wrapper sandwich (two layers):
    Same attack, but attacker can also:
    1. Sandwich at base vault level (if base vault is permissionless)
    2. Sandwich at wrapper level
    3. Exploit timing between wrapper and base vault operations
```

**Impact:** Attack surface increases with each layer. If base vault has premium buffer but wrapper doesn't, attacker can bypass base vault protection by attacking wrapper directly.

**Mitigation:** Apply anti-arbitrage measures (premium buffer, timelock) at the wrapper level, not only at base. Base vault protections don't automatically protect wrapper users from wrapper-level attacks.

## Conditions That Increase Risk

| Condition | Affected Risks | Why |
|-----------|---------------|-----|
| Many wrappers sharing one base | Capacity contention | More competition for limited cap |
| High-frequency deposits/redeems | Double rounding | More operations = more cumulative rounding |
| Base vault is upgradeable | Base vault upgrade | Upgrade can change wrapper behavior silently |
| Base vault has no premium buffer | Sandwich amplification | No protection at base level, wrapper exposed |
| Wrapper lacks fee accrual hook | Fee ordering | Fees calculated incorrectly on every operation |
| Dust deposits allowed | Double rounding | Small amounts lose proportionally more to rounding |
| Base vault has tight capacity | Capacity contention | Wrappers compete for scarce capacity |

## Mitigations Summary

| Risk | Mitigation | Trade-off |
|------|-----------|-----------|
| Double rounding | Minimum deposit threshold | Excludes smallest depositors |
| Capacity contention | Per-wrapper quota or large base cap | Complexity or increased strategy risk |
| Pause propagation | Delegate `maxDeposit`/`maxRedeem` to base | Wrapper loses independent pause control |
| Fee accrual ordering | `_accruePerformanceFee()` before mint/burn | Extra gas per operation (~5K) |
| Preview divergence | Calculate from actual, not preview | Slightly different UX |
| Base vault upgrade | Monitor events + circuit breaker | Operational overhead |
| Sandwich amplification | Premium buffer at wrapper level | Fee on every deposit/redeem |

## Related Patterns

- [Vault Wrapper](./pattern-vault-wrapper.md) — the pattern that introduces these risks
- [Clone Factory](./pattern-clone-factory.md) — multiplies wrappers, amplifying capacity contention
- [Premium Buffer](./pattern-premium-buffer.md) — mitigates sandwich risk at wrapper level
- [High-Water Mark Performance Fee](./pattern-high-water-mark-fee.md) — fee accrual ordering details
- [Circuit Breaker](./pattern-circuit-breaker.md) — can protect against base vault upgrade impact

## References

- [ERC-4626: Tokenized Vaults](https://eips.ethereum.org/EIPS/eip-4626) — composability guarantees and limitations
- [ERC-4626 Security Considerations](https://eips.ethereum.org/EIPS/eip-4626#security-considerations) — spec-level rounding and preview caveats
