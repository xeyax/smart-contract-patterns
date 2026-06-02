# Constant-Product Reserve-Delta AMM

> Price swaps by inferring actual token input from reserve deltas, applying fees, and requiring the constant-product invariant to hold.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, constant-product, reserves, swap, fee |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | High |

## Use When

- A two-asset pool should follow `x * y = k`
- The pair contract can read token balances and maintain internal reserves
- Inputs may arrive before the swap call through a router or direct transfer
- The protocol wants a minimal pool without per-swap callbacks

## Avoid When

- The pool supports concentrated liquidity or many-token invariants
- Token balances cannot be trusted because of rebasing or asynchronous accounting
- The pool needs exact accounting for arbitrary fee-on-transfer tokens

## How It Works

The pair sends requested output, infers input from post-swap balances and prior reserves, then checks the fee-adjusted product:

```solidity
function swap(uint256 amount0Out, uint256 amount1Out, address to) external lock {
    require(amount0Out > 0 || amount1Out > 0, "zero output");
    _transferOut(amount0Out, amount1Out, to);

    uint256 balance0 = token0.balanceOf(address(this));
    uint256 balance1 = token1.balanceOf(address(this));

    uint256 amount0In = balance0 > reserve0 - amount0Out ? balance0 - (reserve0 - amount0Out) : 0;
    uint256 amount1In = balance1 > reserve1 - amount1Out ? balance1 - (reserve1 - amount1Out) : 0;
    require(amount0In > 0 || amount1In > 0, "zero input");

    require(_feeAdjusted(balance0, amount0In) * _feeAdjusted(balance1, amount1In) >= reserve0 * reserve1, "K");
    _updateReserves(balance0, balance1);
}
```

## Key Points

- Infer actual input from balances and reserves instead of trusting router parameters.
- Apply fees to the inferred input before checking `k`.
- Update reserves after the invariant check.
- Lock swap, mint, burn, skim, and sync operations against reentrancy.
- Keep token support assumptions explicit for fee-on-transfer, rebasing, and hook-enabled tokens.
- If the same pool contract supports stable and volatile modes, make the invariant branch explicit and test reserve-delta accounting in both modes.

## Source Evidence

- Uniswap V2 pairs infer swap input from post-transfer balances, apply a 0.3 percent fee adjustment, and require the adjusted product to preserve `k`.
- Aerodrome V1 infers swap input from balance deltas, accrues fees, and enforces volatile or stable `_k` in `/private/tmp/defillama-source/aerodrome-finance__contracts/contracts/Pool.sol`.

## Related Patterns

- [Constant Product AMM Invariants](./req-constant-product-amm-invariants.md)
- [Minimum Liquidity Lock](./pattern-minimum-liquidity-lock.md)
- [Balance Delta Transfer Accounting](../token-integration/pattern-balance-delta-transfer-accounting.md)
