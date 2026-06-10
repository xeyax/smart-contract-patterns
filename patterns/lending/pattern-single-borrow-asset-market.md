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

## Trade-offs

**Pros:**
- Debt, interest, and reserves stay in one base unit, shrinking accounting and liquidation logic versus every-asset borrowing.
- Signed base principal collapses supply and borrow into one field, removing supply-vs-borrow netting edge cases per account.
- Risk is curated per base market, so a bad collateral listing in one market cannot poison unrelated borrow assets.
- Collateral-only operations skip full cross-market accrual via threshold buffers, keeping common paths cheap.

**Cons:**
- Users needing multiple borrow assets must open positions across markets, fragmenting their collateral and liquidity into silos.
- No cross-asset netting: a supplied balance in one market cannot offset debt in another, raising capital requirements for multi-asset users.
- Concentrates protocol solvency on the single base asset; base-asset depeg or failure hits the entire market.
- Each new borrow asset means deploying and curating a whole market, multiplying governance and monitoring overhead.
- Account-scoped siloed-debt variants add transition states (entering/leaving silo) that must reject unrelated borrows correctly or the boundary silently breaks.

## How It Works

Accounts store signed base principal and separate collateral balances:

```solidity
struct Account {
    int104 basePrincipal; // positive supply, negative borrow
    mapping(address => uint128) collateral;
}
```

Supplying the base asset increases principal; borrowing decreases it. Supplying collateral affects only collateral balances and risk capacity.

### Account-Scoped Siloed Debt Variant

Multi-asset lending pools can emulate a single-borrow-asset boundary at the
account level. Once an account borrows a siloed asset, it cannot borrow unrelated
assets until that siloed debt is cleared.

## Key Points

- Keep base supply/borrow accounting separate from collateral token accounting.
- Apply collateral factors only to collateral assets, not to the base principal itself.
- Curate each base market independently.
- Define how protocol reserves absorb base-asset bad debt.
- Document that collateral-only transfers may rely on threshold buffers rather than full cross-market accrual.
- For account-scoped siloed debt, test the transition into and out of siloed debt
  and reject unrelated new debt while the siloed borrow remains open.

## Source Evidence

- Compound III Comet defines one borrowable base token per market, stores signed base principal separately from collateral, and routes base supply/borrow separately from collateral transfers.
- Aave V3 marks siloed borrowing assets in reserve configuration and validates
  that accounts with siloed debt cannot add unrelated borrows in [`contracts/protocol/libraries/configuration/ReserveConfiguration.sol:260`](https://github.com/aave/aave-v3-core/blob/782f51917056a53a2c228701058a6c3fb233684a/contracts/protocol/libraries/configuration/ReserveConfiguration.sol#L260),
  [`contracts/protocol/libraries/configuration/UserConfiguration.sol:137`](https://github.com/aave/aave-v3-core/blob/782f51917056a53a2c228701058a6c3fb233684a/contracts/protocol/libraries/configuration/UserConfiguration.sol#L137),
  and [`contracts/protocol/libraries/logic/ValidationLogic.sol:297`](https://github.com/aave/aave-v3-core/blob/782f51917056a53a2c228701058a6c3fb233684a/contracts/protocol/libraries/logic/ValidationLogic.sol#L297).

## Related Patterns

- [Collateral Threshold Separation Requirements](./req-collateral-threshold-separation.md)
- [Protocol-Absorbed Liquidation Inventory](./pattern-protocol-absorbed-liquidation-inventory.md)
- [Isolated Permissionless Market](./pattern-isolated-permissionless-market.md)
