# Hook-Returned Custom Accounting Deltas

> Let trusted AMM hooks return signed token deltas that the singleton manager settles through the same net-delta ledger as core swaps.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | hooks, accounting, deltas, amm, settlement |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Hooks need to implement fees, wrappers, curves, or other custom accounting
- The core manager can enforce end-of-operation settlement for hook deltas
- Hook capabilities are declared and validated before pool use
- Users and integrators can choose whether to trust a hook-enabled pool

## Avoid When

- Hook code is untrusted but can debit users or pool balances
- The manager cannot distinguish user, pool, and hook deltas
- Returned deltas bypass slippage or authorization checks

## How It Works

After a lifecycle event, the manager applies signed deltas returned by the hook:

```solidity
function _afterSwap(PoolKey memory key, SwapParams memory params) internal {
    (bytes4 selector, int256 userDelta, int256 hookDelta) = key.hook.afterSwap(params);
    require(selector == IHook.afterSwap.selector, "bad selector");

    _accountDelta(msg.sender, key.currency0, userDelta);
    _accountDelta(address(key.hook), key.currency0, hookDelta);
}
```

The operation remains inside the manager's settlement frame, so all hook-created obligations must settle before exit.

## Key Points

- Treat returned deltas as value-moving instructions from trusted hook logic.
- Enforce selector returns and declared hook permissions.
- Apply user slippage checks after custom accounting changes the effective amount.
- Keep hook deltas inside the same settlement invariant as core pool deltas.
- Test malicious or inconsistent hook returns, wrong sign, and unsettled deltas.

## Source Evidence

- Uniswap V4 allows hooks to return custom accounting deltas during liquidity and swap operations while the pool manager remains the common settlement layer.

## Related Patterns

- [Address-Encoded Hook Permissions](./pattern-address-encoded-hook-permissions.md)
- [Net Delta Settlement Invariants](./req-net-delta-settlement-invariants.md)
- [Missing Slippage Protection](../../ANTIPATTERNS.md#missing-slippage-protection)
