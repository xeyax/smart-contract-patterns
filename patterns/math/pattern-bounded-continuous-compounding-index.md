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

## Trade-offs

**Pros:**
- Continuous compounding accrues correctly for any elapsed time without per-block updates or update-frequency-dependent results.
- Storing principal plus a global index keeps per-account state minimal; present value is derived on read.
- Directed rounding per side (user value down, owed debt up) makes approximation error systematically favor protocol solvency.
- Bounded exponent inputs turn approximation error into a provable envelope amenable to fuzzing and formal equivalence checks.

**Cons:**
- Fixed-point exponential approximation is specialist math; review and formal verification cost far exceeds a linear or discrete index.
- Safety depends on enforced input bounds — rate or elapsed-time values outside the proven range produce silently wrong indexes or overflow.
- The update-index-before-rate ordering is an easy-to-miss invariant; violating it retroactively applies the new rate to the past period.
- Narrowing casts after index multiplication (`uint128`, `uint40`) add overflow failure modes that only appear at extreme rates or horizons.
- Reference-model fuzzing and error-envelope tests are a standing maintenance burden whenever the approximation or bounds change.

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
  interest-rate math in [`src/adaptive-curve-irm/libraries/ExpLib.sol:17`](https://github.com/morpho-org/morpho-blue-irm/blob/a1a87fd5a7ee13873ea9d2bbd87e9c7b2cdbbef3/src/adaptive-curve-irm/libraries/ExpLib.sol#L17)
  and [`test/ExpLibTest.sol:19`](https://github.com/morpho-org/morpho-blue-irm/blob/a1a87fd5a7ee13873ea9d2bbd87e9c7b2cdbbef3/test/ExpLibTest.sol#L19).

## Related Patterns

- [Full-Precision Directed Rounding](./pattern-full-precision-directed-rounding.md)
- [Lazy Borrow Index](../lending/pattern-lazy-borrow-index.md)
- [Lazy Reward Index](../rewards/pattern-lazy-reward-index.md)
