# Invariant-Delta Liquidity Accounting

> Mint and burn LP shares from the change in an AMM invariant, with imbalance fees and slippage bounds around the invariant delta.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, liquidity, invariant, lp-token, imbalance-fee |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A pool supports imbalanced or single-sided deposits and withdrawals
- LP shares should represent a claim on the pool invariant rather than raw token sums
- Imbalance costs should be charged to the user causing imbalance
- Proportional-only liquidity is too restrictive for users

## Avoid When

- The pool cannot compute a reliable invariant before and after the operation
- Token values are unrelated and no invariant is meaningful
- Slippage bounds are omitted for mint/burn outcomes

## How It Works

Compute invariant values before and after the operation, apply imbalance fees, then mint or burn against the adjusted delta:

```solidity
D0 = invariant(oldBalances);
D1 = invariant(newBalances);
fees = imbalanceFees(oldBalances, newBalances);
D2 = invariant(newBalances - fees);

minted = totalSupply * (D2 - D0) / D0;
require(minted >= minMintAmount, "slippage");
```

Withdrawals mirror the same structure with `maxBurnAmount` or minimum token outputs.

## Key Points

- Compute fees from imbalance, not only nominal amount.
- Make all user-facing paths specify minimum minted shares, minimum outputs, or maximum burned shares.
- Use internal balances so donations do not change invariant accounting.
- Define rounding direction for invariant delta and fee calculation.
- Test balanced, imbalanced, one-coin, dust, and max-size operations.

## Source Evidence

- Curve pool templates compute `D0`, `D1`, fee-adjusted `D2`, then mint or burn LP shares from the invariant delta for imbalanced liquidity operations.

## Related Patterns

- [Amplified Stable Invariant](./pattern-amplified-stable-invariant.md)
- [Proportional Deposit/Withdrawal](../vaults/pattern-proportional-deposit.md)
- [Missing Slippage Protection](../../ANTIPATTERNS.md#missing-slippage-protection)
