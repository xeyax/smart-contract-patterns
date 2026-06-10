# Kinked Utilization Rate Model

> Increase borrow rates slowly below a target utilization and sharply above it to discourage liquidity exhaustion.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, interest-rate, utilization, liquidity, kink |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- A lending market needs dynamic borrow and supply rates
- High utilization should become expensive before liquidity is exhausted
- The protocol wants a simple transparent rate curve

## Avoid When

- Liquidity is not borrowable or redeemable on demand
- Rates are set entirely off-chain or through auctions
- Asset risk needs multiple discontinuities or nonlinear curves

## Trade-offs

**Pros:**
- Cheap pure-math rate computation — a branch and a multiply — keeps accrual gas low on every interaction.
- The jump slope prices liquidity exhaustion before it happens, protecting supplier withdrawals without admin intervention.
- The curve is transparent and analyzable: integrators and risk teams can predict rates at any utilization.
- Variants (benchmark-targeted, two-kink, hard stop, adaptive) extend the same audited skeleton instead of new mechanisms.

**Cons:**
- Kink, slopes, and base rate are static calibration choices; mis-set parameters either strand liquidity or fail to deter exhaustion until governance reacts.
- Rates respond only to utilization, not external market rates, so the curve can be arbitraged when off-chain yields move (unless a benchmark variant adds oracle-grade dependencies).
- Each added kink or adaptive term multiplies boundary conditions to test — zero cash, exact kinks, full utilization, same-block cap changes.
- Hard utilization stops convert rate pressure into borrow reverts, breaking integrator assumptions near the boundary.
- Benchmark and adaptive variants import oracle freshness, fallback, and bounded-adaptation risks into what was a closed-form model.

## How It Works

Utilization measures how much supplied liquidity is borrowed:

```solidity
utilization = borrows / (cash + borrows - reserves);
```

Borrow rate uses a normal slope below the kink and a steeper jump slope above it:

```solidity
if (utilization <= kink) {
    rate = baseRate + utilization * multiplier;
} else {
    uint256 normalRate = baseRate + kink * multiplier;
    uint256 excess = utilization - kink;
    rate = normalRate + excess * jumpMultiplier;
}
```

### Benchmark-Targeted Variant

Some markets target an external benchmark plus a spread below the kink, then use a steeper utilization component near exhaustion:

```solidity
targetRate = benchmarkRate + spread;

if (utilization <= kink) {
    rate = targetRate * utilization / kink;
} else {
    rate = targetRate + (utilization - kink) * jumpMultiplier;
}
```

The benchmark source needs the same freshness and fallback scrutiny as an oracle.

### Two-Kink Variant

Some markets use three rate regions with two utilization kinks:

```solidity
if (utilization <= kink1) {
    rate = baseRate + utilization * slope1;
} else if (utilization <= kink2) {
    rate = rateAtKink1 + (utilization - kink1) * slope2;
} else {
    rate = rateAtKink2 + (utilization - kink2) * jumpSlope;
}
```

This can model a softer middle region before the final jump rate, but it adds calibration risk.

### Hard Utilization Stop Variant

A second utilization point can be more than a rate kink. A pool may reject new
borrowing above the second point so enough liquidity remains available for exits:

```solidity
require(newUtilization <= u2, "borrow limit");
available = liquidity * (u2 - utilization) / WAD;
```

If governance changes the limit or per-block debt cap, initialize the cap as
fully used for the current block so a limit increase cannot be consumed
atomically before monitoring reacts.

### Adaptive Target-Rate Variant

An interest-rate model can update a target rate from utilization error over time
instead of storing a fixed kink curve. The adaptation must bound the exponential
rate change, clamp minimum and maximum target rates, and make elapsed time part
of the state update so the curve cannot jump outside tested limits.

## Key Points

- Define utilization denominator carefully when reserves are present.
- Keep rates bounded so accrual cannot overflow or make markets unusable.
- Set the kink below the point where withdrawals become unreliable.
- Rate-model updates should be timelocked or otherwise governed.
- Test behavior at zero cash, full utilization, and exactly the kink.
- If the curve uses an external benchmark, validate the benchmark through a bounded rate-source adapter.
- For multi-kink curves, test both kink boundaries and ensure slopes do not create negative or decreasing rates unless that behavior is intentional and bounded.
- For packed or versioned rate data, validate monotonic segment ordering and decode/encode round trips before activating the curve.
- If a utilization point is also a borrow hard stop, test `availableToBorrow`
  around the boundary and ensure exits remain possible when new borrows revert.
- When per-block debt caps change, test same-block borrow attempts immediately
  after the limit update.
- For adaptive curves, bound the target-rate state, utilization error, elapsed
  time, and exponential approximation before the curve can affect borrowing.

## Source Evidence

- JustLend computes utilization from cash, borrows, and reserves, then applies a normal slope before the kink and a jump slope above it.
- SparkLend Advanced uses benchmark-targeted rate-model variants that combine external APR-style inputs, spreads, and kink utilization behavior.
- Venus uses a two-kink interest-rate model and audit material highlights that decreasing supply-rate behavior should be treated as an explicit risk.
- Fluid uses packed one-kink and two-kink rate data variants with validation around rate-data versioning and monotonic curve segments.
- Gearbox V3 uses a second utilization point as an optional borrow hard stop,
  computes available borrow liquidity to reserve exits, and maxes the per-block
  debt cap on limit changes in [`contracts/pool/LinearInterestRateModelV3.sol:13-19`](https://github.com/gearbox-protocol/core-v3/blob/b038597d9070d9fd18593a6ae9c3d28ca931bb73/contracts/pool/LinearInterestRateModelV3.sol#L13-L19),
  [`contracts/pool/LinearInterestRateModelV3.sol:92-142`](https://github.com/gearbox-protocol/core-v3/blob/b038597d9070d9fd18593a6ae9c3d28ca931bb73/contracts/pool/LinearInterestRateModelV3.sol#L92-L142),
  [`contracts/pool/PoolV3.sol:425-469`](https://github.com/gearbox-protocol/core-v3/blob/b038597d9070d9fd18593a6ae9c3d28ca931bb73/contracts/pool/PoolV3.sol#L425-L469),
  and [`contracts/credit/CreditFacadeV3.sol:856-877`](https://github.com/gearbox-protocol/core-v3/blob/b038597d9070d9fd18593a6ae9c3d28ca931bb73/contracts/credit/CreditFacadeV3.sol#L856-L877).
- Morpho Blue adaptive curve IRM updates a bounded target rate from utilization
  error through bounded exponential adaptation in [`src/adaptive-curve-irm/AdaptiveCurveIrm.sol:76`](https://github.com/morpho-org/morpho-blue-irm/blob/a1a87fd5a7ee13873ea9d2bbd87e9c7b2cdbbef3/src/adaptive-curve-irm/AdaptiveCurveIrm.sol#L76)
  and [`src/adaptive-curve-irm/libraries/ConstantsLib.sol:8`](https://github.com/morpho-org/morpho-blue-irm/blob/a1a87fd5a7ee13873ea9d2bbd87e9c7b2cdbbef3/src/adaptive-curve-irm/libraries/ConstantsLib.sol#L8).

## Related Patterns

- [Lazy Borrow Index](./pattern-lazy-borrow-index.md)
- [Comptroller Risk Gate](./pattern-comptroller-risk-gate.md)
- [Bounded Rate Source Adapter](./pattern-bounded-rate-source-adapter.md)
