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

## Trade-offs

**Pros:**
- Quote and execution share one code path, eliminating quote/execution formula drift by construction.
- No duplicated pricing logic to maintain and audit separately.
- Custom-error encoding returns rich structured data (amounts, post-swap price, ticks, gas) without storage writes.
- Works through standard `eth_call`/`callStatic`, so no special node or off-chain infrastructure is required.

**Cons:**
- The function cannot be `view`, so integrators must use low-level static calls and decode revert data instead of normal ABI reads.
- The sentinel revert must fire before any irreversible external effect; a mis-ordered settlement step turns a quote into a live trade.
- Ordinary failures can be mistaken for quote reverts unless callers match the exact error selector — decoding arbitrary revert data yields garbage quotes.
- A quote costs near-full execution gas, making on-chain composition of quotes expensive.
- Simulation mode reachable from normal execution with user funds is a critical failure mode, raising audit stakes.

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

### Snapshot Execution Parity Variant

For Solana AMM routers or other non-EVM systems, snapshot live pool accounts,
load the real program binary into a local simulator, execute the swap, and
compare simulated balance deltas with the quote path. This is not a user-facing
quote API, but it is a strong regression test against quote/execution formula
drift.

### Adapter Account-Meta Parity Variant

AMM adapters can keep quote and execution parity by deriving the execution
account metas from the same adapter state that quote validation uses, then
testing swaps against a simulator with the real program and representative
account snapshots. This is integration evidence, not proof that the underlying
AMM program is correct.

### Swap Callback Quote Variant

AMM quoters can call the real swap entry point, receive the swap callback, and
revert from the callback with encoded amount, post-swap price, initialized tick
crossings, or gas estimate data. Callers must distinguish the expected quote
revert selector from ordinary swap failures.

## Key Points

- Revert before token transfers, state commitments that matter, or external settlement.
- Use a unique custom error selector for quote data.
- Make simulation mode impossible to reach from normal execution with user funds.
- Treat unexpected reverts as failed quotes, not zero-value quotes.
- Test that the simulated path and real path share all pricing and branch logic.
- For swap-callback quotes, include post-swap price or tick metadata when
  integrators need to evaluate price impact, not only amount in/out.
- For snapshot parity tests, pin account snapshots, program binaries, and expected deltas so router or AMM math changes fail loudly.
- For adapter parity tests, assert that quoted routes and executable account metas are generated from the same state snapshot.

## Source Evidence

- Fluid vault liquidation simulation runs the real liquidation path with a sentinel receiver and reverts with encoded quote data before liquidity payback and withdraw settlement.
- Jupiter AMM implementation snapshots AMM accounts, loads real program binaries in LiteSVM, executes swaps, and compares execution deltas to quote results in [`jupiter-core/src/amms/test_harness.rs`](https://github.com/jup-ag/jupiter-amm-implementation/blob/cc068c9d1df0060c62f9a8a4fc37ea13ea7b9b39/jupiter-core/src/amms/test_harness.rs) and `jupiter-core/tests/test_amms.rs`.
- Sanctum's INF Jupiter adapter derives quote and swap account metas from the same adapter state and tests simulated swaps through account snapshots in [`jup-interface/src/lib.rs`](https://github.com/igneous-labs/inf-jup-interface/blob/3f14e9936878916c71213d0cba66e7ad19432728/jup-interface/src/lib.rs) and `jup-interface/tests/common/swap.rs`.
- Uniswap V3 quoters run the swap path and revert from the callback with encoded
  quote data, including V2 metadata for post-swap price, initialized ticks
  crossed, and gas estimate in [`contracts/lens/Quoter.sol:37`](https://github.com/Uniswap/swap-router-contracts/blob/70bc2e40dfca294c1cea9bf67a4036732ee54303/contracts/lens/Quoter.sol#L37),
  [`contracts/lens/QuoterV2.sol:40`](https://github.com/Uniswap/swap-router-contracts/blob/70bc2e40dfca294c1cea9bf67a4036732ee54303/contracts/lens/QuoterV2.sol#L40),
  and [`test/QuoterV2.spec.ts:266`](https://github.com/Uniswap/swap-router-contracts/blob/70bc2e40dfca294c1cea9bf67a4036732ee54303/test/QuoterV2.spec.ts#L266).

## Related Patterns

- [Read-Only Storage Resolver Facade](./pattern-read-only-storage-resolver-facade.md)
- [Read-Only Protocol Health Checker](./pattern-read-only-protocol-health-checker.md)
- [Unchecked External Return](../../ANTIPATTERNS.md#unchecked-external-return)
