# Progressive Protocol Liquidity Limits

> Expand protocol-specific withdrawal and borrow capacity over time while shrinking limits immediately after risk-reducing actions.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, liquidity, limits, throttling, solvency |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Multiple protocol adapters share a liquidity core
- Each adapter needs bounded borrow or withdrawal capacity
- Capacity should recover gradually instead of jumping to a hard cap
- Risk-reducing actions should release pressure immediately

## Avoid When

- A simple static market cap is enough
- The protocol cannot compute limits before every operation
- Limit decay/recovery would make user outcomes unpredictable or unexplainable

## How It Works

For each protocol and asset, compute the current limit from the last stored limit, elapsed time, and configured expansion rate:

```solidity
function currentBorrowLimit(LimitState memory limit) internal view returns (uint256) {
    uint256 expanded = limit.last + (block.timestamp - limit.lastUpdate) * limit.expandPerSecond;
    return min(expanded, limit.max);
}

function operate(int256 borrowDelta, int256 withdrawDelta) external {
    uint256 borrowLimit = currentBorrowLimit(borrowLimits[msg.sender]);
    require(newBorrowAmount <= borrowLimit, "borrow limit");
    _shrinkOrStoreLimitAfterOperation(msg.sender, borrowDelta, withdrawDelta);
}
```

Borrowing and withdrawing consume capacity; repayments and deposits can lower utilization and reset future limits conservatively.

## Key Points

- Scope limits by protocol adapter and asset, not only globally.
- Keep hard maximums separate from time-expanded available limits.
- Shrink limits immediately after capacity-consuming or risk-reducing operations as appropriate.
- Test exact boundary, zero-time, max-time, and underflow cases.
- Do not confuse progressive capacity with request-rate limiting; it is solvency throttling.

## Source Evidence

- Fluid applies per-protocol withdrawal and borrow limits that expand over time, shrink after operations, and remain bounded by hard limits inside the shared liquidity layer.

## Related Patterns

- [Shared Liquidity Kernel](../liquidity/pattern-shared-liquidity-kernel.md)
- [Reserve Exposure Caps](./pattern-reserve-exposure-caps.md)
- [Consumer-Scoped Rate Limiter](../access-control/pattern-consumer-scoped-rate-limiter.md)
