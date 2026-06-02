# Discrete Price-Bin Liquidity Book

> Represent AMM liquidity as shares in discrete price bins and route swaps through the next non-empty bin.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, bin, liquidity-book, discrete-price, shares |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Liquidity should sit at discrete price levels instead of continuous tick ranges
- LPs can deposit one-sided liquidity away from the active price
- Swaps need efficient discovery of the next non-empty bin
- Active-bin deposits require composition fees to avoid value transfer

## Avoid When

- Continuous range liquidity is a better mental model for LPs
- The protocol cannot maintain a safe non-empty-bin index or tree
- One-sided non-active deposits would create unacceptable inventory risk

## Trade-offs

**Pros:**
- Supports concentrated one-sided inventory at specific price bins
- Non-empty-bin trees avoid scanning empty price levels
- Composition fees can protect active-bin LPs from imbalanced joins

**Cons:**
- Bin tree and share accounting are complex
- Active-bin composition and rounding are high-risk math
- LP UX differs from classic constant-product or range AMMs

## How It Works

Each bin stores reserves and LP shares. Swaps consume liquidity at the active bin,
then walk to the next non-empty bin using a tree or bitmap. Non-active bins accept
one-sided deposits on the side implied by their price; active-bin deposits pay
composition fees when they change pool composition.

Inside each bin, the micro-AMM can be constant-sum rather than constant-product:
`L = price * reserveX + reserveY`. Liquidity away from the active bin is
one-sided because the bin is entirely above or below the current price. The
non-empty-bin index must update exactly when a bin crosses between zero and
nonzero liquidity.

```solidity
function swap(SwapState memory state) internal {
    while (state.amountRemaining != 0) {
        Bin storage bin = bins[state.activeBin];
        state.amountRemaining = _swapAgainstBin(bin, state.amountRemaining);
        if (state.amountRemaining != 0) {
            state.activeBin = tree.nextNonEmpty(state.activeBin, state.zeroForOne);
        }
    }
}
```

## Implementation

- Keep bin id, price, reserves, and share math in a single audited library.
- Maintain non-empty-bin tree updates on mint, burn, and swap.
- Enforce one-sided deposits outside the active bin.
- Charge active-bin composition fees when deposits alter reserve ratios.
- Keep constant-sum bin liquidity math, one-sided off-active liquidity rules,
  composition fees, and tree zero-crossing updates in shared libraries.
- Quote code must include every executable liquidity layer in the bin, such as maker liquidity plus processed and open limit orders.
- Exact-out quotes should define where excess rounding goes; assigning multi-unit excess to protocol fees is a fee-policy decision that integrators must match.
- Test empty-bin traversal, tree updates, active-bin fees, share mint/burn rounding, and minimum share locks.

## Source Evidence

- PancakeSwap Infinity Core implements bin pools in `/private/tmp/defillama-source/pancakeswap__infinity-core/src/pool-bin/libraries/BinPool.sol` through `swap`, `mint`, `burn`, and `_mintBins`.
- Bin helper and tree math live in `src/pool-bin/libraries/BinHelper.sol` and `src/pool-bin/libraries/math/TreeMath.sol`.
- PancakeSwap tests bin liquidity behavior in `test/pool-bin/libraries/BinPoolLiquidity.t.sol`.
- Meteora DLMM SDK quote code models bin liquidity layers, exact-in and exact-out fee modes, rounding excess, and bitmap-derived bin-array traversal in `/private/tmp/defillama-source/MeteoraAg_dlmm-sdk/commons/src/quote.rs`, with multi-liquidity quote tests in `ts-client/src/test/swap_quote_multi_liquidity.test.ts`; this is SDK/source-material evidence for quote parity rather than primary proof of the on-chain program.
- Trader Joe V2 Liquidity Book implements constant-sum bin liquidity, one-sided
  off-active bins, active-bin composition fees, and sparse non-empty-bin tree
  transitions in `/private/tmp/defillama-source/traderjoe-xyz__joe-v2/src/libraries/BinHelper.sol:72-164`,
  `/private/tmp/defillama-source/traderjoe-xyz__joe-v2/src/LBPair.sol:480-579`,
  `/private/tmp/defillama-source/traderjoe-xyz__joe-v2/src/LBPair.sol:1070-1112`,
  and `/private/tmp/defillama-source/traderjoe-xyz__joe-v2/src/libraries/math/TreeMath.sol:15-93`.

## Real-World Examples

- PancakeSwap Infinity includes a discrete bin-pool implementation alongside CL-style pools.

## Related Patterns

- [Concentrated Liquidity Ranges](./pattern-concentrated-liquidity-ranges.md)
- [Minimum Liquidity Lock](./pattern-minimum-liquidity-lock.md)
- [Invariant Delta Liquidity Accounting](./pattern-invariant-delta-liquidity-accounting.md)

## References

- PancakeSwap Infinity bin-pool libraries.
