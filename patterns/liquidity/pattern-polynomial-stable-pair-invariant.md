# Polynomial Stable-Pair Invariant

> Price stable-pair swaps with a symmetric polynomial invariant such as `x^3y + y^3x` instead of an amplified `D` invariant.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, stable-pair, invariant, solidly, polynomial |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A two-asset pair should trade near parity or a shared redemption value
- The pool wants a stable curve without a governance-set amplification factor
- Swap math can tolerate bounded iterative solving for the output balance
- The router and pool can expose stable-specific liquidity quotes

## Avoid When

- Assets can diverge permanently and should use volatile `x * y` behavior
- Integrators expect Curve-style amplification semantics
- The implementation cannot bound solver iterations and rounding direction
- Generic liquidity quote helpers would hide stable-specific ratios

## Trade-offs

**Pros:**
- Avoids amplification governance and ramp logic
- Produces tighter pricing near balance than a volatile constant-product pair
- Keeps the invariant local to the pair rather than requiring a multi-asset pool

**Cons:**
- The polynomial solver is less familiar to integrators than `x * y`
- Quote/execution parity depends on using the same stable math everywhere
- Extreme imbalance and dust cases need dedicated tests

## How It Works

The pool normalizes token balances, then computes a stable invariant:

```solidity
function _k(uint256 x, uint256 y) internal pure returns (uint256) {
    return x * y * (x * x + y * y);
}
```

During a swap, the pool solves the new output balance `y` such that the invariant
does not decrease after accounting for the input and fee:

```solidity
uint256 xy = _k(reserve0, reserve1);
uint256 y = _get_y(inputAdjusted, xy, outputReserve);
amountOut = outputReserve - y;
```

The solver should use bounded Newton iterations and deterministic rounding.
Routers should expose stable-specific quote helpers when generic pool quotes
would be misleading for liquidity adds or imbalanced pairs.

## Implementation

### Key Points

- Normalize token decimals before applying the invariant.
- Bound Newton iterations and test convergence at balanced, imbalanced, and dust reserves.
- Use the same invariant functions in quote and execution paths.
- Keep stable and volatile pair types explicit in pool creation and routing.
- Add stable-specific liquidity quote helpers when mint/burn ratios differ from volatile pairs.

## Source Evidence

- Aerodrome V1 implements stable-pair `_f`, `_d`, `_get_y`, and `_k` math in `/private/tmp/defillama-source/aerodrome-finance__contracts/contracts/Pool.sol`.
- Aerodrome router tests check stable pool quote and swap behavior in `/private/tmp/defillama-source/aerodrome-finance__contracts/test/Router.t.sol`.

## Real-World Examples

- Aerodrome V1 - Solidly-style stable pairs using a polynomial invariant for pegged assets.

## Related Patterns

- [Amplified Stable Invariant](./pattern-amplified-stable-invariant.md)
- [Constant-Product Reserve-Delta AMM](./pattern-constant-product-reserve-delta-amm.md)
- [Quote Execution Formula Drift](../../ANTIPATTERNS.md#quote-execution-formula-drift)

## References

- See Source Evidence.
