# Product-Sum Stability Pool Accounting

> Distribute liquidation losses and collateral gains to pooled backstop depositors with global product and sum accumulators.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, stability-pool, liquidation, accumulator, cdp |
| Complexity | High |
| Gas Efficiency | High |
| Audit Risk | High |

## Use When

- A CDP or lending protocol has a pooled liquidation backstop
- Liquidations reduce every depositor's principal pro-rata
- Collateral gains are distributed pro-rata to backstop depositors
- Iterating over all depositors during liquidation is impossible

## Avoid When

- Depositors do not share losses pro-rata
- Losses can exceed pool principal without a separate epoch reset
- Precision, scale changes, and rounding corrections are not thoroughly tested

## Trade-offs

**Pros:**
- Makes liquidation offset O(1) regardless of depositor count
- Keeps depositor gain and remaining-deposit calculation lazy
- Supports frequent liquidations without per-user loops

**Cons:**
- Accumulator math is subtle and precision-sensitive
- Epoch and scale transitions are hard to audit
- Bad rounding can strand dust or overpay gains

## How It Works

The pool stores a global product `P` representing the compounded loss factor and
global sums for collateral gains. Each depositor stores a snapshot when their
deposit changes.

```solidity
function offset(uint256 debtToCancel, uint256 collateralGain) external {
    uint256 lossPerUnit = debtToCancel * DECIMAL_PRECISION / totalDeposits;
    uint256 gainPerUnit = collateralGain * DECIMAL_PRECISION / totalDeposits;

    S = S + gainPerUnit * P;
    P = P * (DECIMAL_PRECISION - lossPerUnit) / DECIMAL_PRECISION;

    if (P < SCALE_FACTOR) {
        _bumpScale();
    }
}

function compoundedDeposit(address user) public view returns (uint256) {
    Snapshot memory s = snapshots[user];
    return initialDeposit[user] * P / s.P;
}
```

Epoch resets handle total pool depletion. Scale changes preserve precision when
the product becomes very small.

## Implementation

- Snapshot product, sum, epoch, and scale for each depositor.
- Reset epoch when the pool is fully depleted.
- Carry rounding error forward instead of leaking it to the next liquidation.
- Test repeated small liquidations, full depletion, scale changes, and all-depositor withdrawal after fuzzed liquidation sequences.
- Keep loss accounting separate from collateral-gain distribution.
- For multi-collateral systems, snapshot and claim each collateral gain accumulator independently and bound user-selected collateral gain claims so one transaction cannot loop over every market.

## Source Evidence

- Liquity V1 implements product/sum accounting in [`packages/contracts/contracts/StabilityPool.sol`](https://github.com/liquity/dev/blob/3e64ee1b52c50d51587c64c1cf75e0ba82934979/packages/contracts/contracts/StabilityPool.sol) through `offset`, `_computeRewardsPerUnitStaked`, `_updateRewardSumAndProduct`, and `_getCompoundedStakeFromSnapshots`.
- Liquity includes rounding and withdrawal tests in `StabilityPoolTest.js`, `StabilityPool_RoundingErrors.js`, and `PoolManager_AllDepositorsCanWithdrawTest.js`.
- Liquity's repository includes `papers/Scalable_Reward_Distribution_with_Compounding_Stakes.tex`, documenting the accumulator approach.
- Liquity V2/Bold keeps the same stability-pool family of accounting mechanics in [`liquity/bold`](https://github.com/liquity/bold/tree/3fcaf602eb36541dd298c73710e067dcad42d8ae).
- Satoshi Core extends the family to multi-collateral gains with epoch/scale/product `P`, per-collateral `S`, reward `G`, and caller-bounded collateral gain claims in [`src/core/StabilityPool.sol`](https://github.com/Satoshi-Protocol/satoshi-core/blob/7f5eddaed965904fde10ea1d40c4c4b3ea118ada/src/core/StabilityPool.sol).

## Real-World Examples

- Liquity V1 and V2 use stability pools as liquidation backstops for CDP debt.

## Related Patterns

- [Explicit Bad Debt Realization](./pattern-explicit-bad-debt-realization.md)
- [Protocol-Absorbed Liquidation Inventory](./pattern-protocol-absorbed-liquidation-inventory.md)
- [Risk-Priority Liquidation Sequencing](./pattern-risk-priority-liquidation-sequencing.md)

## References

- Liquity stability-pool accounting paper in the source repository.
