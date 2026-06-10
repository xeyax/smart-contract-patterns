# Rate-Ordered Redemption Queue

> Let borrower-selected interest rates determine redemption priority, so low-rate debt accepts more redemption risk.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | cdp, redemption, interest-rate, sorted-list, borrower-choice |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Borrowers can choose or adjust their own interest rate
- The stablecoin can be redeemed against borrower collateral
- The protocol wants redemption pressure to price low borrowing rates
- Position ordering can be maintained on-chain with hints or bounded search

## Avoid When

- Redemption priority should be independent of borrower pricing decisions
- The system cannot define fair tie-breaking for equal rates
- Frequent rate changes can grief ordering, fees, or redemption search

## Trade-offs

**Pros:**
- Makes redemption priority an explicit cost of choosing a low rate
- Gives borrowers market feedback without a centralized rate setter
- Can reduce governance dependence for interest-rate calibration

**Cons:**
- Borrower UX is more complex
- Same-rate ordering and rate-change fees become economically important
- Redemptions can concentrate on borrowers that underprice risk

## How It Works

Borrowers choose a rate. Positions are sorted by rate, and redemptions walk the
lowest-rate debt first. When a borrower changes rate or debt, the position is
reinserted into the sorted structure.

```solidity
function setRate(uint256 newRate, address upperHint, address lowerHint) external {
    _chargeUpfrontOrChangeFee(msg.sender, newRate);
    positions[msg.sender].rate = newRate;
    sortedPositions.reInsert(msg.sender, newRate, upperHint, lowerHint);
}

function redeem(uint256 stableAmount) external {
    address current = sortedPositions.lowestRate();
    while (stableAmount != 0 && current != address(0)) {
        stableAmount = _redeemFrom(current, stableAmount);
        current = sortedPositions.next(current);
    }
}
```

## Implementation

- Define deterministic tie-breaking for equal rates.
- Charge or bound rate-change churn so borrowers cannot dodge redemptions for free.
- Keep redemption traversal gas-bounded and resumable.
- Reinsert positions whenever the ordering key changes.
- Test debt in front, equal-rate ordering, partial redemption, and stale hints.

## Source Evidence

- Liquity V2/Bold documents user-set interest rates and redemption ordering in [`README.md`](https://github.com/liquity/bold/blob/3fcaf602eb36541dd298c73710e067dcad42d8ae/README.md).
- Bold maintains sorted troves in [`contracts/src/SortedTroves.sol`](https://github.com/liquity/bold/blob/3fcaf602eb36541dd298c73710e067dcad42d8ae/contracts/src/SortedTroves.sol) and executes redemptions through `RedemptionHelper.sol`.
- Bold tests include `DebtInFrontHelper.t.sol` and `RedemptionHelper.t.sol`.

## Real-World Examples

- Liquity V2/Bold uses borrower-selected interest rates as a redemption-priority signal.

## Related Patterns

- [Hint-Assisted Risk-Ordered Position List](./pattern-hint-assisted-risk-ordered-position-list.md)
- [Collateral Threshold Separation Requirements](./req-collateral-threshold-separation.md)
- [Risk-Priority Liquidation Sequencing](./pattern-risk-priority-liquidation-sequencing.md)

## References

- Liquity V2/Bold borrower operations and redemption helper contracts.
