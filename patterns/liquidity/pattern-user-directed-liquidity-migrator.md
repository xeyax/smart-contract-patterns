# User-Directed Liquidity Migrator

> Atomically pull old LP tokens, remove liquidity, add liquidity to the new pool under user bounds, and refund leftovers.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, liquidity, migration, lp-token, slippage |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Users need to migrate LP positions between pool versions
- The old pool can burn LP tokens for underlying assets in one transaction
- The new pool can mint liquidity from those underlying assets
- Users can provide minimum amounts, deadline, and recipient terms

## Avoid When

- Migration requires protocol custody or operator-controlled batching
- The new pool has incompatible token ordering, fees, or asset semantics
- Users cannot set minimum liquidity or minimum token amounts
- Unused assets cannot be refunded deterministically

## Trade-offs

**Pros:**
- Avoids long-lived migration custody
- Lets each user choose slippage and deadline terms
- Keeps migration atomic from the user's perspective

**Cons:**
- Users still need to approve the migrator for old LP tokens
- Price movement can cause migration to revert
- Migrator code must handle refunds, token ordering, and deadline consistently

## How It Works

The migrator receives old LP tokens from the user, removes liquidity from the old
pool, approves or transfers the received assets into the new pool, mints the new
position, and refunds leftover assets.

```solidity
function migrate(uint256 liquidity, uint256 minA, uint256 minB, uint256 deadline) external {
    oldPair.transferFrom(msg.sender, address(this), liquidity);
    (uint256 amountA, uint256 amountB) = oldRouter.removeLiquidity(liquidity);

    (uint256 usedA, uint256 usedB, uint256 newLiquidity) =
        newRouter.addLiquidity(tokenA, tokenB, amountA, amountB, minA, minB, msg.sender, deadline);

    _refund(tokenA, msg.sender, amountA - usedA);
    _refund(tokenB, msg.sender, amountB - usedB);
}
```

## Implementation

- Pull LP tokens from the user inside the migration transaction.
- Enforce user-provided minimum token amounts, minimum liquidity, and deadline.
- Validate token ordering and target pool identity.
- Refund unused assets to the user or explicit receiver.
- Avoid retaining residual LP or underlying balances after migration.
- Test slippage failure, deadline failure, partial asset use, refund behavior, and token ordering.

## Source Evidence

- QuickSwap periphery includes a V2 migrator that pulls old LP tokens, removes liquidity, adds liquidity to the target pool with user bounds, and refunds leftovers in `/private/tmp/defillama-source/QuickSwap__quickswap-periphery/contracts/UniswapV2Migrator.sol`.
- QuickSwap tests cover migrator behavior in `/private/tmp/defillama-source/QuickSwap__quickswap-periphery/test/UniswapV2Migrator.spec.ts`.

## Real-World Examples

- QuickSwap's UniswapV2-style migrator performs atomic user-directed LP migration.

## Related Patterns

- [Canonical AMM Pool Factory](./pattern-canonical-amm-pool-factory.md)
- [Balance Delta Transfer Accounting](../token-integration/pattern-balance-delta-transfer-accounting.md)
- [Missing Slippage Protection](../../ANTIPATTERNS.md#missing-slippage-protection)

## References

- QuickSwap periphery migrator source.
