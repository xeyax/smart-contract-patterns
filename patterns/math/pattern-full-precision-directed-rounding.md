# Full-Precision Directed Rounding

> Use full-width multiplication/division and explicit rounding direction for financial math where intermediate products can overflow native word size.

## Metadata

| Property | Value |
|----------|-------|
| Category | math |
| Tags | math, rounding, precision, muldiv, invariant |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A formula computes `a * b / denominator` and `a * b` can exceed 256 bits
- Rounding direction determines who receives value
- AMM, lending, or vault invariants rely on exact inequality preservation
- Fuzzing can compare optimized math against a reference model

## Avoid When

- Native-width multiplication cannot overflow by construction
- Approximate rounding is economically irrelevant
- The team cannot maintain low-level arithmetic safely

## How It Works

Use 512-bit intermediate precision and choose rounding explicitly:

```solidity
uint256 amountOut = mulDiv(amountIn, price, Q96);        // round down
uint256 amountIn = mulDivRoundingUp(amountOut, Q96, price);
```

For AMM swaps, use rounding that preserves pool solvency: exact-output input amounts round up, exact-input output amounts round down, and price movement rounds in the direction that prevents overpayment.

## Key Points

- Document rounding direction per formula.
- Keep reference tests for edge values, zero, max values, and denominator boundaries.
- Use full-width math for price conversions before downscaling.
- Pair math libraries with invariant and conservation fuzz tests.
- Do not mix rounding directions across preview and execution paths.
- Check zero denominators before division, including configuration values such as duration or interval length.
- After full-precision calculation, check final narrowing casts instead of assuming the result fits a smaller integer type.
- In claim ledgers, consume/check entitlement with conservative rounding and pay/transfer with the opposite conservative direction so one claimant cannot drain escrow dust owed to later claimants.

## Source Evidence

- Uniswap V3 uses full-precision `mulDiv` and directed AMM rounding libraries, with Echidna tests for full math and swap-step conservation.
- Centrifuge liquidity-pool tests and audit notes show why async claim ledgers need explicit rounding direction across fulfillment and claim paths.
- OnRe's Jupiter integration adapter illustrates why off-chain or adapter quote math should still guard zero interval denominators and final `u128 -> u64` narrowing casts.

## Related Patterns

- [Concentrated Liquidity Invariants](../liquidity/req-concentrated-liquidity-invariants.md)
- [Virtual Share Offset](../vaults/pattern-virtual-share-offset.md)
