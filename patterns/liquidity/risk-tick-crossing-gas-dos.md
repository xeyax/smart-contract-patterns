# Tick Crossing Gas DoS Risk

> Concentrated-liquidity swaps can become gas-expensive when attackers create many initialized ticks that a swap must cross.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, concentrated-liquidity, ticks, gas, dos |
| Type | Risk Description |

## Problem Description

Each initialized tick crossed during a swap can require state reads and writes. If a fee tier allows very dense tick spacing or very small positions, attackers can initialize many ticks and make large swaps unexpectedly expensive or impossible within block gas limits.

## Applies When

- Swap execution loops through initialized ticks
- Tick spacing can be small
- Minimum liquidity per initialized tick is low
- Fee tiers can be added without gas-cost review

## Mitigations

- Bound tick spacing for each fee tier.
- Enforce minimum liquidity or economic cost for initialized ticks.
- Test swaps across many initialized ticks at gas limits.
- Treat new fee tiers and tick spacing changes as high-risk governance actions.
- Use routers that split orders when one route would cross too many ticks.

## Source Evidence

- Uniswap V3 and PancakeSwap V3 audits discuss gas growth from crossing many initialized ticks; PancakeSwap bounds fee-tier tick spacing at the factory level.

## Related Patterns

- [Concentrated Liquidity Invariants](./req-concentrated-liquidity-invariants.md)
- [Unbounded Iteration](../../ANTIPATTERNS.md#unbounded-iteration)
