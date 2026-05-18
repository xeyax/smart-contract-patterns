# Locked Profit Smoothing

> Exclude newly harvested profit from strategy value for a fixed window, then release it linearly to prevent timing extraction around harvests.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, harvest, profit-locking, shares, fairness, timing |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- Strategy profit is realized in discrete harvest transactions
- Deposits can occur immediately before or after harvest
- Share pricing reads strategy value directly
- Existing holders should receive harvested profit over time

## Avoid When

- Yield accrues continuously and cannot be harvested discretely
- The vault already settles deposits asynchronously at epoch NAV
- Profit is too small to justify additional accounting

## Trade-offs

**Pros:**
- Reduces harvest-timing advantage
- Preserves synchronous deposits and withdrawals
- Makes profit release predictable and testable

**Cons:**
- Reported strategy value intentionally lags realized balance
- Requires care around losses during the lock window
- Lock duration becomes an economic parameter

## How It Works

At harvest, record the newly realized profit plus any still-locked profit. Strategy value subtracts the still-locked portion until it decays to zero.

```solidity
function _harvest(uint256 harvestedProfit) internal {
    totalLockedProfit = harvestedProfit + lockedProfit();
    lastHarvest = block.timestamp;
}

function lockedProfit() public view returns (uint256) {
    uint256 elapsed = block.timestamp - lastHarvest;
    if (elapsed >= lockDuration) return 0;

    return totalLockedProfit * (lockDuration - elapsed) / lockDuration;
}

function balanceOfStrategy() public view returns (uint256) {
    return rawStrategyBalance() - lockedProfit();
}
```

### ERC4626 Reward Vesting Variant

For vaults that receive discrete reward deposits, `totalAssets()` can exclude the unvested portion and release it over time:

```solidity
function totalAssets() public view returns (uint256) {
    return rawAssets() - unvestedRewards();
}
```

This has the same fairness goal as strategy locked profit: new depositors should not capture rewards that were earned by earlier holders. The vault must still expose enough information for integrators to understand that `totalAssets()` intentionally lags raw token balance during the vesting window.

### Fixed-Maturity Value Smoothing Variant

For principal tokens or fixed-maturity positions, NAV can otherwise jump as the position approaches deterministic maturity value. Instead of waiting for a maturity cliff, value the position at a conservative discounted maturity amount and release the remaining yield linearly until maturity:

```solidity
function assets() public view returns (uint256) {
    return discountedMaturityValue() - remainingYieldToMaturity();
}
```

Recompute the accrual rate whenever the principal-token balance changes. This is not generic continuous-yield smoothing; it is for known maturity payoff curves with explicit early-exit and loss behavior.

## Key Points

- Lock only profit, not principal.
- Carry forward previously locked profit when harvesting again.
- Release linearly unless a different curve has a clear economic reason.
- Define loss behavior explicitly: losses should not be hidden by locked profit accounting.
- Use with actual-received deposit accounting; it does not fix fee-on-transfer tokens.
- For ERC4626 reward vesting, make sure preview functions use the same vested-asset view as deposits and redemptions.
- For fixed-maturity positions, use conservative maturity assumptions and update smoothing state whenever principal balance changes.

## Source Evidence

- Beefy strategies set locked profit during harvest, linearly decay it over `lockDuration`, and subtract it from strategy `balanceOf()`.
- Beefy tests verify a later depositor cannot capture freshly harvested profit and that locked profit unlocks after the duration.
- Ethena-style ERC4626 reward vaults exclude unvested rewards from `totalAssets()` and release them over time so incoming users do not receive already-earned rewards.
- infiniFi's Pendle farm values principal tokens at discounted maturity value, subtracts remaining yield, and releases that yield over time to avoid a deterministic maturity NAV cliff.

## Related Patterns

- [Vault Fairness Requirements](./req-vault-fairness.md) - R4 timing advantage
- [Delta NAV Share Accounting](./pattern-delta-nav.md) - base share accounting
- [Async Deposit/Withdrawal](./pattern-async-deposit.md) - stronger timing mitigation
