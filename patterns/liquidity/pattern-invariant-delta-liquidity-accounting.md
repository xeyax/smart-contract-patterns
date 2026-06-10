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

## Trade-offs

**Pros:**
- Supports single-sided and imbalanced deposits/withdrawals without letting users extract value from existing LPs.
- Imbalance fees charge the cost of skew to the user who creates it, instead of socializing it across the pool.
- LP shares track the invariant rather than raw token sums, so share value stays meaningful as balances skew.
- Internal-balance accounting makes donations and external transfers inert, closing free-mint paths.

**Cons:**
- Three invariant evaluations per operation (`D0`, `D1`, `D2`) make liquidity changes markedly more gas-expensive than proportional mint/burn, especially with iterative invariant solvers.
- Rounding direction must be fixed per step of the delta and fee math; a single wrong direction leaks value to or from LPs over many operations.
- Maintaining stored balances parallel to token balances doubles the accounting state that can drift and must be reconciled.
- Fee-adjusted delta math is hard to review and demands a wide test matrix: balanced, imbalanced, one-coin, dust, and max-size operations.
- If the invariant solver fails to converge or the invariant is misconfigured, every liquidity path is blocked or mispriced at once.

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
- Keep stored/internal balances separate from raw token balances so donations,
  rebases, or external transfers do not mint free LP shares.
- Test balanced, imbalanced, one-coin, dust, and max-size operations.

## Source Evidence

- Curve pool templates compute `D0`, `D1`, fee-adjusted `D2`, then mint or burn LP shares from the invariant delta for imbalanced liquidity operations.
- Curve StableSwap NG computes `D0`, `D1`, and fee-adjusted liquidity deltas for
  deposits and withdrawals while using stored balances for donation-resistant
  accounting in [`contracts/main/CurveStableSwapNG.vy:1077-1125`](https://github.com/curvefi/stableswap-ng/blob/2abe778f40206a6c0fd108a0a53ad3266cbedeee/contracts/main/CurveStableSwapNG.vy#L1077-L1125)
  and [`contracts/main/CurveStableSwapNG.vy:1185-1205`](https://github.com/curvefi/stableswap-ng/blob/2abe778f40206a6c0fd108a0a53ad3266cbedeee/contracts/main/CurveStableSwapNG.vy#L1185-L1205).

## Related Patterns

- [Amplified Stable Invariant](./pattern-amplified-stable-invariant.md)
- [Proportional Deposit/Withdrawal](../vaults/pattern-proportional-deposit.md)
- [Missing Slippage Protection](../../ANTIPATTERNS.md#missing-slippage-protection)
