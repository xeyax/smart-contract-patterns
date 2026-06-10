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
- The migrator is an owner-set farm escape hatch that can replace pooled LP tokens for every staker

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
- For savings-vault or receipt-token migrations, redeem the old position under user authorization, measure the actual base-asset balance delta, then deposit into the new vault for the same user.
- Avoid farm-level migrators that receive approval over the pool's full LP balance and replace custody on behalf of all users unless the migrator is one-shot, timelocked, audited, and user exit remains available.
- Test slippage failure, deadline failure, partial asset use, refund behavior, and token ordering.

## Source Evidence

- QuickSwap periphery includes a V2 migrator that pulls old LP tokens, removes liquidity, adds liquidity to the target pool with user bounds, and refunds leftovers in [`contracts/UniswapV2Migrator.sol`](https://github.com/QuickSwap/quickswap-periphery/blob/522a94168b0814d0776d834119df377f03898807/contracts/UniswapV2Migrator.sol).
- QuickSwap tests cover migrator behavior in [`test/UniswapV2Migrator.spec.ts`](https://github.com/QuickSwap/quickswap-periphery/blob/522a94168b0814d0776d834119df377f03898807/test/UniswapV2Migrator.spec.ts).
- Reservoir's sRUSD migration contract pulls old sRUSD from the user, redeems through the old saving module, measures actual rUSD received, and deposits into the new ERC4626 vault for the user in [`src/Migration.sol`](https://github.com/reservoir-protocol/srusd/blob/cc34c9ecb30eaf13d567df42f6d9bd165e4c2914/src/Migration.sol).
- VVS Farm's owner-set `migrate` path approves the migrator for a pool's full LP balance and accepts replacement LP tokens if the returned balance matches in [`contracts/Craftsman.sol`](https://github.com/vvs-finance/vvs-farm/blob/acd79b99d88157b9d520eeac92e8c6424ae9d8de/contracts/Craftsman.sol), a contrasting privileged-custody risk.

## Real-World Examples

- QuickSwap's UniswapV2-style migrator performs atomic user-directed LP migration.

## Related Patterns

- [Canonical AMM Pool Factory](./pattern-canonical-amm-pool-factory.md)
- [Balance Delta Transfer Accounting](../token-integration/pattern-balance-delta-transfer-accounting.md)
- [Missing Slippage Protection](../../ANTIPATTERNS.md#missing-slippage-protection)

## References

- QuickSwap periphery migrator source.
