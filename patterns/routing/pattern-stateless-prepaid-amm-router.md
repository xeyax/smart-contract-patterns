# Stateless Prepaid AMM Router

> Route AMM swaps by pre-paying the first pair, forwarding intermediate outputs pair-to-pair, and enforcing user slippage at the router boundary.

## Metadata

| Property | Value |
|----------|-------|
| Category | routing |
| Tags | routing, amm, swap, slippage, deadline |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- Pools infer swap input from received token balances
- The router should not hold balances after the transaction
- Multi-hop swaps can send each hop's output directly to the next pair
- Users need exact-input or exact-output bounds plus deadlines

## Avoid When

- Pools require callback-based settlement
- Tokens may take transfer fees on arbitrary hops without a supporting path
- The router must custody user balances across transactions

## How It Works

For exact-input swaps, the router computes expected amounts, transfers input to the first pair, then chains pair outputs:

```solidity
function swapExactTokensForTokens(uint256 amountIn, uint256 minOut, address[] calldata path, address to, uint256 deadline) external {
    require(block.timestamp <= deadline, "expired");
    uint256[] memory amounts = getAmountsOut(amountIn, path);
    require(amounts[amounts.length - 1] >= minOut, "slippage");

    token(path[0]).transferFrom(msg.sender, pairFor(path[0], path[1]), amountIn);
    _swap(amounts, path, to);
}
```

Intermediate outputs are sent to the next pair, while the final output goes to the receiver.

## Key Points

- Enforce `amountOutMin`, `amountInMax`, and deadline at entry.
- Derive pair addresses deterministically from token pairs.
- Send intermediate outputs directly to the next pair.
- Guard native-asset receive functions so only the wrapped-native token can send funds.
- Refund unused native-asset dust on exact-output paths.

## Source Evidence

- Uniswap V2 Router02 pre-transfers input to the first pair, routes intermediate outputs directly to following pairs, enforces slippage and deadlines, guards WETH receive, and refunds ETH dust.

## Related Patterns

- [Constant-Product Reserve-Delta AMM](../liquidity/pattern-constant-product-reserve-delta-amm.md)
- [Canonical AMM Pool Factory](../liquidity/pattern-canonical-amm-pool-factory.md)
- [Missing Slippage Protection](../../ANTIPATTERNS.md#missing-slippage-protection)
