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

## Trade-offs

**Pros:**
- Bounds the damage of a compromised or buggy adapter to its time-expanded capacity instead of the whole shared liquidity pool.
- Capacity recovers automatically over time, avoiding governance round-trips that a static cap would require after every shock.
- Immediate shrink after risk-reducing actions releases pressure without waiting for the expansion clock.
- Per-protocol, per-asset scoping gives finer-grained solvency throttling than one global cap.

**Cons:**
- Limit computation runs before every operation, adding gas and a new revert path to all borrow/withdraw flows.
- Time-expansion, shrink, and reset logic is full of boundary bugs: zero-elapsed-time, max-time, and underflow cases all need explicit tests.
- Without liquidation-scoped exemptions the limiter can trap liquidators holding seized collateral, turning a safety device into a solvency hazard.
- Users can hit opaque "limit" reverts whose available capacity depends on elapsed time and other actors' recent operations, making outcomes hard to predict.
- Misconfigured expansion rates or hard maximums silently recreate either an open spigot or a frozen market; parameters need ongoing operational review.

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
- Define explicit liquidation-scoped exemptions when the limiter would otherwise trap liquidators holding seized collateral or collateral tokens.
- If limits can be disabled for upgrade compatibility, make the disabled mode explicit and test both enabled and disabled flows.
- Test exact boundary, zero-time, max-time, and underflow cases.
- Do not confuse progressive capacity with request-rate limiting; it is solvency throttling.

## Source Evidence

- Fluid applies per-protocol withdrawal and borrow limits that expand over time, shrink after operations, and remain bounded by hard limits inside the shared liquidity layer.
- Suilend implements Move `RateLimiter` logic and liquidation-scoped exemptions in [`contracts/suilend/sources/rate_limiter.move`](https://github.com/suilend/suilend/blob/d5ba83a617bb0778b48b0c3b1e77a87be81258ca/contracts/suilend/sources/rate_limiter.move) and `lending_market.move`.
- Suilend tests liquidation exemption behavior in [`contracts/suilend/tests/lending_market_tests.move`](https://github.com/suilend/suilend/blob/d5ba83a617bb0778b48b0c3b1e77a87be81258ca/contracts/suilend/tests/lending_market_tests.move).
- Solend SPL Token Lending implements reserve and market outflow rate limits in [`token-lending/sdk/src/state/rate_limiter.rs`](https://github.com/solendprotocol/solana-program-library/blob/d04ce00bbf4356c4fd32b3be38eb9760b696bb3e/token-lending/sdk/src/state/rate_limiter.rs) and tests them in `token-lending/program/tests/outflow_rate_limits.rs`.

## Related Patterns

- [Shared Liquidity Kernel](../liquidity/pattern-shared-liquidity-kernel.md)
- [Reserve Exposure Caps](./pattern-reserve-exposure-caps.md)
- [Consumer-Scoped Rate Limiter](../access-control/pattern-consumer-scoped-rate-limiter.md)
