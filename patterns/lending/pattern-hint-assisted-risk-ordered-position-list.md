# Hint-Assisted Risk-Ordered Position List

> Maintain liquidation or redemption priority in a sorted position list while callers supply hints to avoid full scans.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | cdp, sorted-list, liquidation, redemption, hints |
| Complexity | High |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- Position priority depends on a sortable risk metric such as collateral ratio or interest rate
- Liquidations or redemptions must process positions in deterministic order
- The active position set can be too large for on-chain search
- Callers can derive approximate insert hints off-chain

## Avoid When

- Exact ordering is not required for protocol safety or economics
- Stale hints can place positions incorrectly without verification
- The ordering metric can change without repositioning the node

## Trade-offs

**Pros:**
- Avoids unbounded scans over all positions
- Preserves deterministic priority for liquidations or redemptions
- Lets off-chain search reduce on-chain cost without trusting the caller

**Cons:**
- Hints are part of the user experience and integration surface
- Reinsertions must be called whenever the ordering metric changes
- Linked-list corruption can block high-value operations

## How It Works

The protocol stores positions in a doubly linked list sorted by the risk metric.
Callers provide upper and lower hints. The contract verifies that the final
location is valid before inserting or reinserting.

```solidity
function adjustPosition(uint256 newDebt, uint256 newCollateral, address upper, address lower) external {
    uint256 newRatio = collateralRatio(newDebt, newCollateral);
    sortedPositions.reInsert(msg.sender, newRatio, upper, lower);
}

function findInsertPosition(uint256 ratio, address upper, address lower) public view returns (address, address) {
    if (_validInsertPosition(ratio, upper, lower)) return (upper, lower);
    return _walkFromNearestHint(ratio, upper, lower);
}
```

## Implementation

- Validate every caller-provided hint before using it.
- Keep insert and reinsert paths symmetric.
- Reposition when collateral, debt, rate, or any ordering field changes.
- Provide helper views that return approximate hints for integrators.
- For multi-collateral CDPs, keep one ordered list per collateral or market so hints cannot cross risk domains.
- Test head, tail, equal-key, stale-hint, and removal cases.

## Source Evidence

- Liquity V1 uses [`packages/contracts/contracts/SortedTroves.sol`](https://github.com/liquity/dev/blob/3e64ee1b52c50d51587c64c1cf75e0ba82934979/packages/contracts/contracts/SortedTroves.sol) with `insert`, `reInsert`, and `findInsertPosition`.
- Liquity V1 helper logic in `HintHelpers.sol` exposes `getApproxHint` and `getRedemptionHints`.
- Liquity tests include `SortedTrovesTest.js` for ordering and list behavior.
- Liquity V2/Bold uses analogous sorted trove machinery in [`contracts/src/SortedTroves.sol`](https://github.com/liquity/bold/blob/3fcaf602eb36541dd298c73710e067dcad42d8ae/contracts/src/SortedTroves.sol).
- Satoshi Core uses per-collateral NICR-ordered trove lists with caller hints and redemption hint helpers in [`src/core/SortedTroves.sol`](https://github.com/Satoshi-Protocol/satoshi-core/blob/7f5eddaed965904fde10ea1d40c4c4b3ea118ada/src/core/SortedTroves.sol) and `src/helpers/MultiCollateralHintHelpers.sol`.

## Real-World Examples

- Liquity uses sorted troves to support liquidation and redemption ordering without looping across all borrowers.

## Related Patterns

- [Risk-Priority Liquidation Sequencing](./pattern-risk-priority-liquidation-sequencing.md)
- [Rate-Ordered Redemption Queue](./pattern-rate-ordered-redemption-queue.md)
- [Unbounded Iteration](../../ANTIPATTERNS.md#unbounded-iteration)

## References

- Liquity V1 and V2 sorted trove implementations.
