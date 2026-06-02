# Bounded Continuous Compounding Index

> Accrue continuously compounded balances with a bounded fixed-point exponential approximation and explicit rounding direction.

## Metadata

| Property | Value |
|----------|-------|
| Category | math |
| Tags | math, index, compounding, fixed-point, rounding |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Balances accrue at a continuously compounded rate
- The protocol stores principal and derives present value through an index
- Rate, time, and exponent inputs have enforceable upper bounds
- Formal, fuzz, or reference tests can cover approximation error and casts

## Avoid When

- Rate or elapsed time can exceed the approximation's safe input range
- Rounding direction is not tied to who receives value
- Native-width multiplication can overflow without a proven bound
- A simpler linear or discrete index is accurate enough

## How It Works

Update the global index from the previous timestamp before storing a new rate:

```solidity
function currentIndex() public view returns (uint128) {
    uint256 elapsed = block.timestamp - latestIndexTimestamp;
    uint256 factor = expBounded(rate * elapsed);
    return uint128(index * factor / EXP_SCALE);
}

function updateRate(uint32 newRate) external onlyRateOracle {
    index = currentIndex();
    latestIndexTimestamp = uint40(block.timestamp);
    rate = newRate;
}
```

Use opposite conservative rounding directions for assets owed to the protocol and assets owed to users. For example, earning-token present value rounds down, while debt or owed principal rounds up.

## Key Points

- Bound `rate * elapsed` before calling the exponential approximation.
- Document approximation error and how it is allocated.
- Update the index before changing the rate.
- Check narrowing casts after index multiplication.
- Pair optimized math with reference-model fuzzing or formal equivalence checks.
- Native-width arithmetic is acceptable only when every range and cast is proven or exhaustively tested.
- If using a fixed-point exponential for adaptive rates rather than account
  balances, clip exponent inputs to the approximation's proven range and test the
  error envelope around both positive and negative bounds.

## Source Evidence

- M0 updates continuous indexes before rate changes, computes `e^(rate*time)` with bounded fixed-point math, rounds earning-token index multiplication down and owed-debt multiplication up, and tests/explores math equivalence against reference models.
- Morpho Blue IRM clips `wExp` inputs and tests approximation error for adaptive
  interest-rate math in `/private/tmp/defillama-source/morpho-org__morpho-blue-irm/src/adaptive-curve-irm/libraries/ExpLib.sol:17`
  and `/private/tmp/defillama-source/morpho-org__morpho-blue-irm/test/ExpLibTest.sol:19`.

## Related Patterns

- [Full-Precision Directed Rounding](./pattern-full-precision-directed-rounding.md)
- [Lazy Borrow Index](../lending/pattern-lazy-borrow-index.md)
- [Lazy Reward Index](../rewards/pattern-lazy-reward-index.md)
