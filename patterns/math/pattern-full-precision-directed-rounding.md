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

## Trade-offs

**Pros:**
- 512-bit intermediates eliminate silent overflow in `a * b / d`, allowing high-precision prices and scales without artificial input caps.
- Explicit per-formula rounding direction makes value-flow bias a documented design decision instead of an accident.
- Directed rounding preserves solvency inequalities (round inputs up, outputs down), closing dust-extraction loops in AMMs, vaults, and claim ledgers.
- Optimized libraries pair naturally with reference-model fuzzing, giving strong equivalence evidence for the hot-path math.

**Cons:**
- `mulDiv`-style assembly is dense low-level code that few reviewers can verify by inspection; teams inherit a maintenance obligation for it.
- Rounding direction must be tracked per call site; mixing directions across preview and execution paths creates exploitable preview/settle mismatches.
- Full-width math costs more gas than naive multiply-divide on paths where overflow was never possible.
- Correct full-precision results can still overflow final narrowing casts, adding a failure mode after the "safe" math.
- Conservative rounding accumulates dust in the protocol's favor that may need explicit sweeping or accounting treatment.

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
- Cross-domain amount conversion should document direction-specific rounding: deposits and outgoing debits usually round down to avoid over-crediting, while withdrawals or externally owed amounts may need to round up to avoid underpaying the user.

## Source Evidence

- Uniswap V3 uses full-precision `mulDiv` and directed AMM rounding libraries, with Echidna tests for full math and swap-step conservation.
- Centrifuge liquidity-pool tests and audit notes show why async claim ledgers need explicit rounding direction across fulfillment and claim paths.
- OnRe's Jupiter integration adapter illustrates why off-chain or adapter quote math should still guard zero interval denominators and final `u128 -> u64` narrowing casts.
- Kinetiq converts HYPE/kHYPE amounts to the 8-decimal L1 operation format with explicit `roundUp` behavior, rounding deposits down and withdrawal obligations up in [`src/StakingManager.sol`](https://github.com/code-423n4/2025-04-kinetiq/blob/a3913ca2b9d021df45a428e0185ee4f4f45509ae/src/StakingManager.sol).

## Related Patterns

- [Concentrated Liquidity Invariants](../liquidity/req-concentrated-liquidity-invariants.md)
- [Virtual Share Offset](../vaults/pattern-virtual-share-offset.md)
