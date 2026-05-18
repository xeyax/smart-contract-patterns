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

## Key Points

- Define utilization denominator carefully when reserves are present.
- Keep rates bounded so accrual cannot overflow or make markets unusable.
- Set the kink below the point where withdrawals become unreliable.
- Rate-model updates should be timelocked or otherwise governed.
- Test behavior at zero cash, full utilization, and exactly the kink.

## Source Evidence

- JustLend computes utilization from cash, borrows, and reserves, then applies a normal slope before the kink and a jump slope above it.

## Related Patterns

- [Lazy Borrow Index](./pattern-lazy-borrow-index.md)
- [Comptroller Risk Gate](./pattern-comptroller-risk-gate.md)
