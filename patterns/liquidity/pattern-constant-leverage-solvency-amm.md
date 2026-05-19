# Constant-Leverage Solvency AMM

> Price swaps through a leveraged debt/collateral AMM while checking that the final virtual solvency value stays inside the allowed envelope.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, leverage, solvency, debt, invariant |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A pool represents a leveraged collateral/debt position instead of a simple token reserve pair
- Swaps can change collateral, debt, or LP exposure and must preserve protocol solvency
- The AMM has an oracle price used to compute a conservative post-trade value
- Liquidation or deleveraging logic depends on the same solvency boundary

## Avoid When

- A constant-product or stableswap invariant fully describes pool safety
- The oracle can be manipulated in the same transaction as the swap
- The protocol cannot explain who absorbs losses when the solvency envelope is breached
- The final-state check depends on stale accounting or unchecked external callbacks

## Trade-offs

**Pros:**
- Makes leveraged AMM safety explicit instead of relying on reserve conservation alone
- Gives audits a concrete post-trade inequality to fuzz
- Can support swaps that rebalance debt and collateral atomically

**Cons:**
- Depends on robust oracle and debt accounting
- More complex than reserve-only AMM invariants
- Bad rounding direction can turn the envelope check into false safety

## How It Works

The AMM derives a virtual solvency value from oracle price, collateral, debt, and leverage. Every swap computes the post-trade state and rejects it unless the conservative value is at least the required boundary:

```solidity
function swap(uint256 amountIn, bool stableIn, uint256 minOut) external returns (uint256 amountOut) {
    State memory beforeState = _loadState();
    uint256 price = oracle.price();

    State memory afterState = _simulateSwap(beforeState, price, amountIn, stableIn);

    require(_solvencyValue(afterState, price, true) >= beforeState.solvencyFloor, "bad final state");
    amountOut = _settle(afterState, amountIn, minOut);
}
```

The key is that the invariant is not only "tokens in equals tokens out". It is "after the trade, the leveraged pool can still satisfy the conservative debt/collateral solvency equation".

### Flash-Liquidity Swap Variant

Some leveraged AMMs need temporary stablecoin liquidity to execute the virtual swap. A wrapper can compute the required flash amount, take the loan, perform the AMM action, and repay before returning output:

```solidity
function exchange(uint256 i, uint256 j, uint256 amountIn, uint256 minOut) external {
    uint256 flashAmount = _requiredFlashAmount(i, amountIn);
    flashLender.flashLoan(address(this), stablecoin, flashAmount, abi.encode(i, j, amountIn, minOut));
}
```

Treat the flash wrapper as part of the AMM invariant. Verify callback caller, initiator, loan token, repayment amount, and post-swap solvency in one frame.

## Implementation

### Key Points

- Define the solvency equation in terms of current debt, collateral, leverage, and oracle price.
- Use conservative rounding: outputs down, required inputs and debt coverage up.
- Recompute the post-trade value after all reserve and debt changes.
- Make oracle freshness and deviation checks part of the swap precondition.
- Fuzz swaps against a reference model that includes extreme price, low-liquidity, and near-insolvent states.
- If flash liquidity is used, include flash callback authentication and repayment in the invariant tests.

## Source Evidence

- Yield Basis `AMM.vy` computes leveraged position state through `get_x0`, updates collateral and debt around `exchange`, and checks the final conservative `get_x0(..., True)` against the pre-trade boundary in `/private/tmp/defillama-source/Peter-Brad__2025-08-yield-basis-Peter-Brad-public/contracts/AMM.vy`.
- Yield Basis `VirtualPool.vy` computes flash amounts in `_calculate`, authenticates the flash lender in `onFlashLoan`, performs virtual swaps through `exchange`, and repays from the post-swap balance in `/private/tmp/defillama-source/Peter-Brad__2025-08-yield-basis-Peter-Brad-public/contracts/VirtualPool.vy`.
- Yield Basis tests exercise AMM statefulness and virtual-pool flash flows under `/private/tmp/defillama-source/Peter-Brad__2025-08-yield-basis-Peter-Brad-public/tests/amm` and `tests/lt/test_virtual_pool.py`.

## Real-World Examples

- Yield Basis - leveraged LP AMM with post-trade solvency envelope and optional flash-backed virtual pool execution.

## Related Patterns

- [Fixed-Yield Implied-Rate AMM](./pattern-fixed-yield-implied-rate-amm.md)
- [Constant Product Reserve Delta AMM](./pattern-constant-product-reserve-delta-amm.md)
- [Conservative AMM LP Collateral Oracle](../oracles/pattern-conservative-amm-lp-collateral-oracle.md)
- [Full-Precision Directed Rounding](../math/pattern-full-precision-directed-rounding.md)

## References

- See Source Evidence.
