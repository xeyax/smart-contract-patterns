# Dual-Mode Collateral Shares

> Split supplied collateral into protected non-borrowable shares and borrowable collateral shares with explicit transitions between modes.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, collateral, shares, isolation, liquidation |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Users can supply assets either as passive protected collateral or as collateral that backs debt
- Borrowable collateral needs interest, solvency, and liquidation accounting
- Protected deposits should be insulated from borrower-specific debt risk
- Liquidation must consume borrowable collateral before protected collateral

## Avoid When

- All supplied assets should be fungible within one collateral pool
- Mode transitions cannot run solvency and liquidity checks
- Hooks or integrations can bypass the mode boundary
- Liquidation priority would be unclear to users

## Trade-offs

**Pros:**
- Lets passive suppliers avoid lending their assets into borrower risk
- Makes collateral-mode changes auditable
- Gives liquidators deterministic priority over collateral buckets

**Cons:**
- Adds share-token and accounting complexity
- Mode transitions become value-bearing state changes
- Integrations must distinguish the two share classes

## How It Works

Deposits mint either protected shares or collateral shares. Moving protected
shares into borrowable collateral burns one mode and mints the other under
solvency and liquidity checks:

```solidity
function depositProtected(uint256 assets, address owner) external {
    protectedShares[owner] += _toShares(assets);
    _transferIn(assets);
}

function transitionToCollateral(uint256 protectedShareAmount) external {
    _burnProtected(msg.sender, protectedShareAmount);
    _mintCollateral(msg.sender, protectedShareAmount);
    _checkSolvency(msg.sender);
}

function liquidationOrder(address borrower) internal view returns (Bucket[] memory) {
    return _borrowableCollateralFirst(borrower);
}
```

## Implementation

### Key Points

- Use separate accounting for protected and borrowable collateral shares.
- Run action-scoped oracle and solvency checks when moving into or out of borrowable mode.
- Define liquidation priority across collateral buckets.
- Ensure hooks cannot transfer or borrow through the wrong mode.
- Test transitions, borrow attempts against protected shares, liquidation priority, and pause behavior.

## Source Evidence

- Silo V2 defines protected collateral and collateral share tokens in [`silo-core/contracts/SiloConfig.sol`](https://github.com/silo-finance/silo-contracts-v2/blob/fd1c73beafb7c81f77cd4477002ebadb4142d243/silo-core/contracts/SiloConfig.sol).
- Silo V2 action logic handles deposit and transition flows in [`silo-core/contracts/lib/Actions.sol`](https://github.com/silo-finance/silo-contracts-v2/blob/fd1c73beafb7c81f77cd4477002ebadb4142d243/silo-core/contracts/lib/Actions.sol).
- Silo V2 liquidation priority and close-factor behavior are implemented in [`silo-core/contracts/hooks/liquidation/lib/PartialLiquidationLib.sol`](https://github.com/silo-finance/silo-contracts-v2/blob/fd1c73beafb7c81f77cd4477002ebadb4142d243/silo-core/contracts/hooks/liquidation/lib/PartialLiquidationLib.sol).
- Silo V2 hook documentation describes collateral-type behaviors in [`silo-core/docs/Hooks.md`](https://github.com/silo-finance/silo-contracts-v2/blob/fd1c73beafb7c81f77cd4477002ebadb4142d243/silo-core/docs/Hooks.md).

## Real-World Examples

- Silo V2 - isolated markets separate protected collateral from collateral that can back borrowing.

## Related Patterns

- [Single Borrow Asset Market](./pattern-single-borrow-asset-market.md)
- [Isolated Permissionless Market](./pattern-isolated-permissionless-market.md)
- [Dust-Aware Liquidation Cap](./pattern-dust-aware-liquidation-cap.md)

## References

- See Source Evidence.
