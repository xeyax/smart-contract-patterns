# Stateless Callback-Validated Swap Router

> Route swaps through compact path data and callback validation while keeping user slippage, deadline, and payer rules at the router boundary.

## Metadata

| Property | Value |
|----------|-------|
| Category | routing |
| Tags | routing, swap, callback, slippage, path |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- Swaps may traverse one or more canonical AMM pools
- Pool settlement happens through callbacks
- The router should not custody funds longer than one transaction
- Users need exact-input and exact-output slippage bounds

## Avoid When

- Pool identity cannot be derived and validated in callbacks
- The router stores long-lived balances or approvals without accounting
- Paths are too dynamic to parse safely on-chain

## How It Works

Encode the route as packed token/fee hops, then validate the callback sender before paying the owed pool:

```solidity
function swap(bytes calldata path, uint256 amountIn, uint256 minOut, uint256 deadline) external {
    require(block.timestamp <= deadline, "expired");
    uint256 amountOut = _swapPath(path, amountIn, msg.sender);
    require(amountOut >= minOut, "slippage");
}

function swapCallback(int256 amount0Delta, int256 amount1Delta, bytes calldata data) external {
    PoolKey memory key = decodeFirstPool(data);
    require(msg.sender == computePool(factory, key), "bad pool");
    _payOwedPool(key, amount0Delta, amount1Delta);
}
```

## Key Points

- Enforce deadline and exact-in/exact-out bounds at the router entry point.
- Validate callback sender against factory-derived pool identity.
- Switch payer deliberately between user and router for multi-hop paths.
- Avoid storing route state between calls.
- Test path decoding, wrong callback sender, expired deadline, and slippage failure.

## Source Evidence

- PancakeSwap V3 routers use compact path encoding, exact-input/exact-output bounds, deadlines, payer switching, and callback validation against canonical pool identity.

## Related Patterns

- [Canonical AMM Pool Factory](../liquidity/pattern-canonical-amm-pool-factory.md)
- [Verified Callback Settlement](../liquidity/pattern-verified-callback-settlement.md)
- [Missing Slippage Protection](../../ANTIPATTERNS.md#missing-slippage-protection)
