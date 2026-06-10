# Coverage-Ratio Gated Tranche Exits

> Gate junior exits and senior inflows by tranche coverage so first-loss capital cannot quietly leave when senior protection is thin.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, tranche, coverage, junior, exit |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A vault has senior and junior share classes
- Junior capital is intended to absorb first loss or protect senior claims
- Exit terms should degrade gradually before a hard exit block
- Coverage can be computed from current assets and tranche liabilities

## Avoid When

- All vault shares absorb losses pro rata
- Coverage can be manipulated cheaply around deposits or redemptions
- Junior share price can approach zero without minimum-share or pause guards
- Users need fixed withdrawal terms independent of tranche health

## Trade-offs

**Pros:**
- Keeps first-loss capacity in the vault when senior protection is low
- Gives users softer warning states through fees or cooldowns before denial
- Makes senior deposit and junior exit health checks explicit

**Cons:**
- Coverage can be timing-sensitive around large deposits, redemptions, or accounting updates
- Exit fees and locks are harder for users to predict
- Bad coverage formulas can create griefing or frozen junior exits

## How It Works

Compute current coverage from senior liabilities, junior assets, or a configured junior-to-senior ratio. Map the coverage band to an exit mode: ordinary ERC4626 redemption, redemption with a fee, share-lock cooldown, or blocked exit.

```solidity
function previewJuniorExit(uint256 shares) public view returns (ExitTerms memory terms) {
    uint256 coverage = currentCoverageRatio();

    if (coverage < hardBlockRatio) {
        revert("coverage");
    }
    if (coverage < lockRatio) {
        return ExitTerms({mode: ExitMode.LockedShares, feeBps: 0, cooldown: longCooldown});
    }
    if (coverage < feeRatio) {
        return ExitTerms({mode: ExitMode.Fee, feeBps: exitFeeBps, cooldown: 0});
    }
    return ExitTerms({mode: ExitMode.Instant, feeBps: 0, cooldown: 0});
}
```

Senior deposits can use a higher buffer than junior withdrawals so new senior inflows do not enter when junior protection is already thin.

## Implementation

### Key Points

- Define the coverage ratio and the exact assets/liabilities included in it.
- Use separate thresholds for junior exits and senior deposits when needed.
- Stage exit modes from fee to lock to denial instead of relying only on a hard revert.
- Test large senior deposits or withdrawals immediately before junior exits.
- Add minimum-share, minimum-price, or pause thresholds for extreme junior price states.
- Treat accounting updates that change coverage as value-affecting operations.

## Source Evidence

- Strata computes junior withdrawal capacity and senior deposit caps from coverage ratios in [`contracts/tranches/Accounting.sol`](https://github.com/Strata-Markets/contracts/blob/6441c75d9b8fcc0056fc34ca2b7ab8b57346fe56/contracts/tranches/Accounting.sol).
- Strata maps current coverage to fee, ERC4626, or share-lock exit modes in [`contracts/tranches/StrataCDO.sol`](https://github.com/Strata-Markets/contracts/blob/6441c75d9b8fcc0056fc34ca2b7ab8b57346fe56/contracts/tranches/StrataCDO.sol) and configures coverage bands in [`contracts/tranches/base/cooldown/SharesCooldown.sol`](https://github.com/Strata-Markets/contracts/blob/6441c75d9b8fcc0056fc34ca2b7ab8b57346fe56/contracts/tranches/base/cooldown/SharesCooldown.sol).
- Strata tests coverage-dependent junior redemption fees and locks in [`test/tranches/cooldowns/Exit.spec.ts`](https://github.com/Strata-Markets/contracts/blob/6441c75d9b8fcc0056fc34ca2b7ab8b57346fe56/test/tranches/cooldowns/Exit.spec.ts), and PoC tests under [`test/PoC`](https://github.com/Strata-Markets/contracts/blob/6441c75d9b8fcc0056fc34ca2b7ab8b57346fe56/test/PoC) show that deposits, accounting updates, and low junior prices can manipulate coverage if thresholds are not guarded.

## Real-World Examples

- Strata Markets applies coverage-dependent exit modes to tranched vault redemptions.

## Related Patterns

- [Tiered Loss Waterfall Requirements](./req-tiered-loss-waterfall.md)
- [Async Deposit/Withdrawal](./pattern-async-deposit.md)
- [Vault Fairness Requirements](./req-vault-fairness.md)

## References

- See Source Evidence.
