# Zero-Liquidity Price Control Risk

> In concentrated-liquidity AMMs, swaps through empty ranges can move pool price without meaningful liquidity-backed trading.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, concentrated-liquidity, zero-liquidity, price, risk |
| Type | Risk Description |

## Problem Description

When active liquidity is zero or near zero, a swap loop may still move price toward the user's limit or next initialized tick. That can let an attacker control pool state or seed oracle observations without paying the cost implied by healthy liquidity.

## Applies When

- Active liquidity can become zero inside the valid tick range
- Swaps are allowed while no range is active
- Other protocols read the pool price or TWAP without liquidity checks
- Price limits are the only guard on swap movement

## Failure Modes

- A pool price is moved cheaply before liquidity appears.
- TWAP observations include zero-liquidity price states.
- Dependent protocols trust price without checking harmonic mean liquidity.

## Mitigations

- Require minimum liquidity before using pool prices for value-bearing operations.
- Include harmonic mean liquidity in TWAP oracle reads.
- Reject or ignore observations from pools with insufficient active liquidity.
- Initialize pools and liquidity atomically where possible.

## Source Evidence

- Uniswap V3 and PancakeSwap V3 audit material identifies zero-liquidity swap price control risk in concentrated-liquidity pools.

## Related Patterns

- [TWAP Oracle](../oracles/pattern-twap-oracle.md)
- [Concentrated Liquidity Invariants](./req-concentrated-liquidity-invariants.md)
- [Price Manipulation Risk](../oracles/risk-price-manipulation.md)
