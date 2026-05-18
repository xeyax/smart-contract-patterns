# Single Borrow-Asset Market

> Build each lending market around one borrowable base asset with separate collateral assets, reducing cross-asset borrow complexity.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, market, base-asset, collateral, comet |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- The protocol wants one borrow asset per market
- Collateral assets are volatile but debt accounting should stay in one base unit
- Risk can be curated per base market
- Simpler liquidation and reserve accounting is preferred over every-asset borrowing

## Avoid When

- Users need to borrow many assets from the same collateral pool
- Cross-asset netting is a core product requirement
- A single base asset creates unacceptable concentration risk

## How It Works

Accounts store signed base principal and separate collateral balances:

```solidity
struct Account {
    int104 basePrincipal; // positive supply, negative borrow
    mapping(address => uint128) collateral;
}
```

Supplying the base asset increases principal; borrowing decreases it. Supplying collateral affects only collateral balances and risk capacity.

## Key Points

- Keep base supply/borrow accounting separate from collateral token accounting.
- Apply collateral factors only to collateral assets, not to the base principal itself.
- Curate each base market independently.
- Define how protocol reserves absorb base-asset bad debt.
- Document that collateral-only transfers may rely on threshold buffers rather than full cross-market accrual.

## Source Evidence

- Compound III Comet defines one borrowable base token per market, stores signed base principal separately from collateral, and routes base supply/borrow separately from collateral transfers.

## Related Patterns

- [Collateral Threshold Separation Requirements](./req-collateral-threshold-separation.md)
- [Protocol-Absorbed Liquidation Inventory](./pattern-protocol-absorbed-liquidation-inventory.md)
- [Isolated Permissionless Market](./pattern-isolated-permissionless-market.md)
