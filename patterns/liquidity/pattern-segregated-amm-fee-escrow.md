# Segregated AMM Fee Escrow

> Move swap fees out of AMM reserves into a separate fee escrow and lazily index claimable fees for LP holders.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, fee, lp, lazy-accounting, reserve |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- LP fees should be claimable separately instead of auto-compounded into reserves
- Pool invariant reserves must remain distinct from accrued fee balances
- LP token transfers need to carry accrued fee entitlement cleanly
- Fee claims can tolerate lazy per-account checkpointing

## Avoid When

- Fees are intentionally left in the pool to increase LP token price
- LP transfers cannot update fee indexes
- The pool cannot separate reserve accounting from token balances
- Claimable fee tokens may be arbitrary unsafe reward tokens

## Trade-offs

**Pros:**
- Keeps invariant reserves separate from claimable LP fees
- Lets LPs claim fees without burning liquidity
- Reuses lazy reward-index mechanics

**Cons:**
- Requires transfer hooks or balance-change checkpoints
- Adds a fee escrow contract and claim path
- Misordered reserve and fee updates can desynchronize accounting

## How It Works

The pool sends swap fees into a dedicated escrow instead of counting them as
reserves. A global fee index tracks accumulated fee entitlement per LP token, and
each LP account is checkpointed before mint, burn, transfer, or claim.

```solidity
function _accountFee(address token, uint256 amount) internal {
    if (totalSupply() == 0) return;
    feeIndex[token] += amount * 1e18 / totalSupply();
    IERC20(token).transfer(address(poolFees), amount);
}

function _updateFor(address account) internal {
    uint256 balance = balanceOf(account);
    accrued0[account] += balance * (feeIndex[token0] - userIndex0[account]) / 1e18;
    accrued1[account] += balance * (feeIndex[token1] - userIndex1[account]) / 1e18;
    userIndex0[account] = feeIndex[token0];
    userIndex1[account] = feeIndex[token1];
}
```

## Implementation

- Keep fee balances out of the reserves used by swap invariant math.
- Checkpoint sender and receiver before LP token transfers.
- Checkpoint LPs before minting, burning, and fee claims.
- Make the escrow pay only proven accrued fees, not arbitrary token balances.
- Test swaps, mints, burns, transfers, claims, and zero-supply periods.
- Restrict escrow claims to the owning pool so users cannot call fee-transfer helpers directly.

## Source Evidence

- Velodrome V2 removes fees from pool reserves, indexes fee entitlement per LP holder, and pays through `PoolFees` in [`contracts/Pool.sol`](https://github.com/velodrome-finance/contracts/blob/b3065d8b6702b14b094f9f6046b752cc9f78c43b/contracts/Pool.sol) and `contracts/PoolFees.sol`.
- Velodrome tests cover fee claiming and LP-transfer accounting in [`test/PoolFees.t.sol`](https://github.com/velodrome-finance/contracts/blob/b3065d8b6702b14b094f9f6046b752cc9f78c43b/test/PoolFees.t.sol).
- Aerodrome V1 moves fees into a separate `PoolFees` contract and restricts fee claims to the pool in [`contracts/Pool.sol`](https://github.com/aerodrome-finance/contracts/blob/1ba30815bba620f7e9faa34769ffd00c214c9b82/contracts/Pool.sol) and [`contracts/PoolFees.sol`](https://github.com/aerodrome-finance/contracts/blob/1ba30815bba620f7e9faa34769ffd00c214c9b82/contracts/PoolFees.sol).

## Real-World Examples

- Velodrome V2 - segregated AMM fee escrow with LP fee indexes.

## Related Patterns

- [Lazy Reward Index](../rewards/pattern-lazy-reward-index.md)
- [Constant Product Reserve-Delta AMM](./pattern-constant-product-reserve-delta-amm.md)
- [Invariant Delta Liquidity Accounting](./pattern-invariant-delta-liquidity-accounting.md)

## References

- See Source Evidence.
