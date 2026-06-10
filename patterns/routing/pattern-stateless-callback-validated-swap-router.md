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

## Trade-offs

**Pros:**
- No long-lived custody or stored route state — the router holds funds for at most one transaction, shrinking the loss surface.
- Factory-derived callback validation lets pools pull payment without trusting caller-supplied identity.
- Compact packed paths make multi-hop swaps cheaper than per-hop approvals and transfers through the router.
- User protections (deadline, exact-in/exact-out bounds) stay at one entry boundary regardless of route complexity.

**Cons:**
- Callback-validation mistakes are catastrophic: any flaw in pool-identity derivation lets a fake pool drain payer approvals.
- Path decoding and payer switching across hops are byte-level logic with a high test burden (wrong sender, reversed hops, expired deadlines).
- Allow-revert command plans move cleanup into the plan; a missing sweep, balance-check, or refund command strands user funds in the router.
- Multi-hop exact-output economics can drift when only an aggregate final bound is enforced, requiring per-hop limits.
- Only works with AMMs whose settlement is callback-based and whose pool identity is derivable on-chain.

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

In action-router variants, the router enters the pool manager's unlock callback, dispatches a compact list of actions, and derives the user from transient locker state while keeping final slippage checks at the router boundary.

Command-plan routers can also mark selected commands as allowed to revert. That
is useful for partial fills, but it moves cleanup into the command plan: every
allow-revert branch needs explicit sweep, balance-check, or refund commands so a
failed subplan cannot strand user funds in the router.

## Key Points

- Enforce deadline and exact-in/exact-out bounds at the router entry point.
- Validate callback sender against factory-derived pool identity.
- Switch payer deliberately between user and router for multi-hop paths.
- Avoid storing route state between calls.
- For unlock-based action routers, validate the pool manager caller, constrain the action set, and enforce final plus per-hop slippage after callback settlement.
- For command-plan routers with partial-revert commands, require explicit
  cleanup commands and test the failure branch, not only the successful route.
- For multi-hop exact-output routes, test reversed-hop execution and enforce hop
  bounds where intermediate route choices can change execution price.
- For aggregator swap routers, allowlist both the callable target selector and
  any separate approval spender; source-side bridge swaps should not inherit a
  destination executor's broader arbitrary-call surface.
- Test path decoding, wrong callback sender, expired deadline, and slippage failure.

## Source Evidence

- PancakeSwap V3 routers use compact path encoding, exact-input/exact-output bounds, deadlines, payer switching, and callback validation against canonical pool identity.
- Uniswap V4 periphery validates pool-manager callbacks, executes action batches inside unlock, tracks the transient locker sender, and enforces final and per-hop slippage checks.
- Uniswap Universal Router uses command bytes with an allow-revert flag and
  payment/sweep modules, making explicit cleanup part of safe partial fills in
  [`README.md:40`](https://github.com/Uniswap/universal-router/blob/5a5336a2aa69faea5407ad610feabed6d5a1c4fa/README.md#L40),
  [`contracts/UniversalRouter.sol:70`](https://github.com/Uniswap/universal-router/blob/5a5336a2aa69faea5407ad610feabed6d5a1c4fa/contracts/UniversalRouter.sol#L70),
  [`contracts/base/Dispatcher.sol:303`](https://github.com/Uniswap/universal-router/blob/5a5336a2aa69faea5407ad610feabed6d5a1c4fa/contracts/base/Dispatcher.sol#L303),
  and [`contracts/modules/Payments.sol:75`](https://github.com/Uniswap/universal-router/blob/5a5336a2aa69faea5407ad610feabed6d5a1c4fa/contracts/modules/Payments.sol#L75).
- Uniswap Universal Router V2/V3 modules enforce per-hop swap bounds and test
  exact-output reversed-hop behavior in [`contracts/modules/uniswap/v3/V3SwapRouter.sol:107`](https://github.com/Uniswap/universal-router/blob/5a5336a2aa69faea5407ad610feabed6d5a1c4fa/contracts/modules/uniswap/v3/V3SwapRouter.sol#L107),
  [`contracts/modules/uniswap/v2/V2SwapRouter.sol:44`](https://github.com/Uniswap/universal-router/blob/5a5336a2aa69faea5407ad610feabed6d5a1c4fa/contracts/modules/uniswap/v2/V2SwapRouter.sol#L44),
  and [`test/foundry-tests/UniswapV3.t.sol:180`](https://github.com/Uniswap/universal-router/blob/5a5336a2aa69faea5407ad610feabed6d5a1c4fa/test/foundry-tests/UniswapV3.t.sol#L180).
- LI.FI swap helpers validate contract-selector allowlists, approve-only spenders, minimum received amounts, no-leftover behavior, and direct ERC20Proxy call rejection in [`src/Libraries/LibAllowList.sol`](https://github.com/lifinance/contracts/blob/7aeb2419d52d6bf834bf2c47e54dd8ea470a57bd/src/Libraries/LibAllowList.sol), `src/Helpers/SwapperV2.sol`, `src/Libraries/LibSwap.sol`, and `src/Periphery/Executor.sol`.

## Related Patterns

- [Canonical AMM Pool Factory](../liquidity/pattern-canonical-amm-pool-factory.md)
- [Verified Callback Settlement](../liquidity/pattern-verified-callback-settlement.md)
- [Selector-Scoped Authority](../access-control/pattern-selector-scoped-authority.md)
- [Missing Slippage Protection](../../ANTIPATTERNS.md#missing-slippage-protection)
