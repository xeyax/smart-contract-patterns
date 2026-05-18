# Front-Runnable Pool Initialization Risk

> A public one-shot AMM pool initialization lets an attacker set the first price before legitimate liquidity arrives.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, initialization, price, frontrun, risk |
| Type | Risk Description |

## Problem Description

Some AMM pools are deployed before their initial price is set. If `initialize(price)` is public and can only be called once, any account can set the starting price. A front-runner can initialize at an extreme price, causing first liquidity providers, routers, or dependent protocols to operate against a hostile initial state.

## Applies When

- Pool deployment and price initialization are separate transactions
- Initialization is public and one-shot
- The first liquidity add assumes a fair starting price
- Periphery can create or initialize an existing pool opportunistically

## Failure Modes

- First LP deposits at a manipulated initial price.
- Integrators assume canonical pool existence implies sane price.
- A malicious initial price becomes the anchor for early TWAP observations.

## Mitigations

- Atomically create, initialize, and add first liquidity through trusted periphery.
- Require first-liquidity slippage bounds based on the expected initial price.
- Monitor uninitialized canonical pools and initialize them before advertising support.
- Treat early TWAP observations as unsafe until sufficient trading history exists.

## Source Evidence

- Uniswap V3 and PancakeSwap V3 pools expose public one-shot initialization, and Trail of Bits/SlowMist audit material flags price-initialization front-running risk.

## Related Patterns

- [Canonical AMM Pool Factory](./pattern-canonical-amm-pool-factory.md)
- [TWAP Oracle](../oracles/pattern-twap-oracle.md)
- [Mempool-Visible Value Transfer](../../ANTIPATTERNS.md#mempool-visible-value-transfer)
