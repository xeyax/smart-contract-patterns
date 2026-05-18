# Compressed Amount Storage With Directional Rounding

> Store large lending amounts in compressed form only when every rounding direction is explicit, conservative, and tested at dust boundaries.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, storage, rounding, compression, accounting |
| Complexity | High |
| Gas Efficiency | High |
| Audit Risk | High |

## Use When

- A lending core packs many amounts into storage-constrained slots
- Exact full-precision storage would be too expensive
- Rounding can be chosen to favor protocol solvency or user safety by path
- Minimum amounts can make dust behavior explicit

## Avoid When

- Lossy storage can accumulate unbounded accounting error
- Rounding direction is undocumented or differs between preview and execution
- Users can exploit compression by repeatedly cycling dust operations

## How It Works

Convert exact amounts into a compact mantissa/exponent representation, but choose the rounding direction by operation:

```solidity
function storeBorrowAmount(uint256 exact) internal pure returns (uint256 packed) {
    return BigMath.toPacked(exact, RoundUp);
}

function storeSupplyAmount(uint256 exact) internal pure returns (uint256 packed) {
    return BigMath.toPacked(exact, RoundDown);
}

function deposit(uint256 amount) external {
    require(amount >= minDeposit, "dust");
    uint256 packed = storeSupplyAmount(amount);
    require(packed != oldPackedAmount, "no storage change");
}
```

## Key Points

- Document rounding direction for supply, withdraw, borrow, repay, interest, and limits.
- Add minimum operation sizes when compression would otherwise erase a change.
- Revert no-op storage changes that would take user funds without changing accounting.
- Fuzz around exponent boundaries and smallest representable amounts.
- Separate compressed-storage risk from full-precision arithmetic risk.

## Source Evidence

- Fluid uses BigMath-style compressed liquidity amounts, path-specific rounding, minimum deposits, and tests around borrow and withdraw limit rounding.

## Related Patterns

- [Full-Precision Directed Rounding](../math/pattern-full-precision-directed-rounding.md)
- [Lending Accounting Freshness Requirements](./req-lending-accounting-freshness.md)
- [Dust-Aware Liquidation Cap](./pattern-dust-aware-liquidation-cap.md)
