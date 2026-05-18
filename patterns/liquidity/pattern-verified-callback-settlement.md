# Verified Callback Settlement

> Let AMM pools optimistically call external payers during mint, swap, or flash operations, then verify post-callback balances before finalizing.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, callback, settlement, swap, flash |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- The pool needs optimistic settlement for swaps, mints, or flash loans
- Callers can source payment from arbitrary contracts during the callback
- The pool can verify token balance deltas after the callback
- Callback callers can verify the canonical pool address

## Avoid When

- Token balance checks cannot reliably prove payment
- Reentrancy locks cannot span the full operation
- Callback payloads are allowed to control critical pool state

## How It Works

The pool transfers or accounts optimistically, calls the user callback, then checks that the required token balance was paid:

```solidity
uint256 balanceBefore = token.balanceOf(address(this));
ICallback(msg.sender).swapCallback(amount0Owed, amount1Owed, data);
require(token.balanceOf(address(this)) >= balanceBefore + amountOwed, "underpaid");
```

Periphery callback handlers validate `msg.sender` against the canonical factory-derived pool before paying.

## Key Points

- Lock the pool for the full callback-settlement operation.
- Verify post-callback balances for each owed token.
- Bind callback caller to token pair, fee tier, and factory.
- Avoid writes to critical invariant state after untrusted callbacks unless they are already locked and accounted.
- Test underpayment, wrong-callback-caller, reentrancy, and fee-on-transfer token assumptions.

## Source Evidence

- Uniswap V3 and PancakeSwap V3 use optimistic mint/swap/flash callbacks, pool-wide locks, callback caller validation, and post-callback balance checks with underpayment tests.

## Related Patterns

- [Canonical AMM Pool Factory](./pattern-canonical-amm-pool-factory.md)
- [Balance Delta Transfer Accounting](../token-integration/pattern-balance-delta-transfer-accounting.md)
- [Hook/Callback Trust](../../ANTIPATTERNS.md#hookcallback-trust)
