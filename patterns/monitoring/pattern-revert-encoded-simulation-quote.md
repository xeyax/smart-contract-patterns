# Revert-Encoded Simulation Quote

> Run the real mutating path in a simulation call, then intentionally revert with encoded quote data before irreversible settlement.

## Metadata

| Property | Value |
|----------|-------|
| Category | monitoring |
| Tags | simulation, quote, revert, resolver, liquidation |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A quote depends on the same branching logic as execution
- Duplicating quote logic would drift from the real path
- Callers can use `eth_call`, `callStatic`, or resolver decoding for custom errors
- The simulated path can revert before irreversible external effects

## Avoid When

- The path performs external settlement before the sentinel revert
- Callers expect a normal `view` function
- Revert data can be confused with arbitrary failure data

## How It Works

The simulation enters the real path with a sentinel receiver and reverts with structured quote data before settlement:

```solidity
error LiquidationQuote(uint256 repayAmount, uint256 collateralOut);

function simulateLiquidate(Position calldata position) external {
    (uint256 repay, uint256 out) = _liquidate(position, DEAD_ADDRESS, SimulationMode.QuoteOnly);
    revert LiquidationQuote(repay, out);
}
```

Resolvers call the function statically, catch the custom error, and decode the quote.

## Key Points

- Revert before token transfers, state commitments that matter, or external settlement.
- Use a unique custom error selector for quote data.
- Make simulation mode impossible to reach from normal execution with user funds.
- Treat unexpected reverts as failed quotes, not zero-value quotes.
- Test that the simulated path and real path share all pricing and branch logic.

## Source Evidence

- Fluid vault liquidation simulation runs the real liquidation path with a sentinel receiver and reverts with encoded quote data before liquidity payback and withdraw settlement.

## Related Patterns

- [Read-Only Storage Resolver Facade](./pattern-read-only-storage-resolver-facade.md)
- [Read-Only Protocol Health Checker](./pattern-read-only-protocol-health-checker.md)
- [Unchecked External Return](../../ANTIPATTERNS.md#unchecked-external-return)
