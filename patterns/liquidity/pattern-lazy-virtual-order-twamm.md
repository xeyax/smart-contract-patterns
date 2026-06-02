# Lazy Virtual-Order TWAMM

> Execute long-term AMM orders lazily in virtual intervals before ordinary pool actions observe reserves.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | liquidity, amm, twamm, virtual-orders, long-term-orders |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Users need to split large swaps across time inside an AMM
- Executing every interval eagerly would be too expensive
- Pool mint, burn, swap, cancel, and withdraw paths can all settle virtual orders first
- Long-term order proceeds can be tracked by reward factors or cumulative pool state

## Avoid When

- The pool cannot afford complex reserve accounting
- Long-term order execution can be skipped before price-sensitive actions
- Users need guaranteed per-block execution rather than lazy catch-up
- Pause design would block order cancellation or matured proceeds withdrawal

## Trade-offs

**Pros:**
- Reduces price impact for large orders
- Avoids keeper-only execution for every interval
- Lets any later interaction catch up virtual order state

**Cons:**
- More reserve and order-pool state than a normal AMM
- Long inactive periods can create large catch-up work
- Pause and cancellation paths need careful liveness rules

## How It Works

Long-term orders add a sales rate to one side's order pool and an expiration interval. Before ordinary AMM actions, the pool executes virtual orders through the target timestamp:

```solidity
modifier executeVirtualOrdersFirst() {
    _executeVirtualOrders(block.timestamp);
    _;
}

function longTermSwap(uint256 amountIn, uint256 intervals)
    external
    executeVirtualOrdersFirst
    returns (uint256 orderId)
{
    orderId = _openLongTermOrder(msg.sender, amountIn, intervals);
}
```

The virtual execution updates AMM reserves, long-term order reward factors, and expired sales rates. Users later cancel active orders or withdraw proceeds from expired orders.

## Implementation

```solidity
function swap(uint256 amountOut, address to) external executeVirtualOrdersFirst {
    _constantProductSwap(amountOut, to);
}

function withdrawProceeds(uint256 orderId) external executeVirtualOrdersFirst {
    uint256 proceeds = _claimableProceeds(orderId);
    _markClaimed(orderId);
    _transferProceeds(msg.sender, proceeds);
}
```

### Key Points

- Execute virtual orders before every reserve-sensitive action.
- Track separate order-pool state for each direction.
- Align expiries to intervals so execution is bounded and deterministic.
- Keep cancellation and proceeds withdrawal available when new order placement is paused.
- Test inactivity catch-up, simultaneous opposite-side orders, cancellation, leftovers, and pause recovery.

## Source Evidence

- Fraxswap `FraxswapPair` opens long-term swaps, executes virtual orders before core pool actions, and exposes cancellation and proceeds withdrawal in `/private/tmp/defillama-source/FraxFinance__frax-solidity/src/hardhat/contracts/Fraxswap/core/FraxswapPair.sol`.
- Fraxswap `LongTermOrders` tracks order pools, sales rates, reward factors, expiries, and lazy virtual execution in `/private/tmp/defillama-source/FraxFinance__frax-solidity/src/hardhat/contracts/Fraxswap/twamm/LongTermOrders.sol`.
- Fraxswap tests cover single-sided, two-sided, cancellation, leftovers, inactivity, brick recovery, and pause-with-withdraw behavior under `/private/tmp/defillama-source/FraxFinance__frax-solidity/src/hardhat/test/Fraxswap`.

## Real-World Examples

- Fraxswap - Uniswap V2-style AMM with lazy virtual-order TWAMM support.

## Related Patterns

- [Constant Product Reserve-Delta AMM](./pattern-constant-product-reserve-delta-amm.md)
- [Balance-Delta Transfer Accounting](../token-integration/pattern-balance-delta-transfer-accounting.md)
- [TWAP Oracle](../oracles/pattern-twap-oracle.md)

## References

- See Source Evidence.
