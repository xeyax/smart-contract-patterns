# Withdrawal Liquidity Buffer

> Reserve enough liquid assets for claims, route new inflows to queued withdrawal deficits first, and only deploy surplus capital.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, withdrawals, buffer, liquidity, queue, liveness |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Vault assets are deployed into illiquid, staked, or externally managed positions
- Users can queue withdrawals before assets are fully liquid
- The protocol wants to reduce withdrawal starvation without holding all assets idle
- New deposits can refill pending withdrawal deficits

## Avoid When

- All assets are always liquid and withdrawal settlement is immediate
- Holding a buffer would create unacceptable idle yield drag
- The system cannot reliably distinguish promised claims from free liquidity

## Trade-offs

**Pros:**
- Improves exit liveness during normal operation
- Prevents new deposits from being deployed while old exits are underfunded
- Makes queued withdrawal deficits explicit

**Cons:**
- Idle buffer reduces capital efficiency
- Buffer sizing is a governance/risk parameter
- Does not eliminate queue risk under severe stress

## How It Works

The vault tracks three amounts:

```solidity
availableToWithdraw = liquidBalance - claimReserve;
bufferDeficit = targetBuffer > availableToWithdraw
    ? targetBuffer - availableToWithdraw
    : 0;
queueDeficit = pendingWithdrawalAssets - availableToWithdraw;
withdrawDeficit = max(bufferDeficit, queueDeficit);
```

New deposits or protocol withdrawals first refill the deficit:

```solidity
function handleIncomingAssets(uint256 amount) internal {
    uint256 deficit = getWithdrawDeficit();
    uint256 toBuffer = amount < deficit ? amount : deficit;

    _increaseWithdrawalLiquidity(toBuffer);
    _deploySurplus(amount - toBuffer);
}
```

For externally redeemed assets with minimum lot sizes, the buffer can top up by redeeming at least the external minimum lot when local cash is insufficient:

```solidity
if (cash < requested) {
    uint256 needed = requested - cash;
    uint256 redeemAmount = max(needed, externalMinRedeemLot);
    uint256 beforeBalance = asset.balanceOf(address(this));
    _redeemExternal(redeemAmount);
    require(asset.balanceOf(address(this)) - beforeBalance >= needed, "redeem shortfall");
}
```

Any surplus from a minimum-lot redemption is buffer liquidity, not admin-free cash, until all pending claims and low-watermark requirements are satisfied.

## Key Points

- `claimReserve` must be subtracted from free liquidity; already-promised claims are not deployable capital.
- Deficit-first routing should apply to both new deposits and strategy withdrawals.
- Buffer target and drawdown floor should be explicit risk parameters.
- Instant withdrawals can charge a utilization-based fee as the buffer approaches the floor.
- Queued withdrawals still need gas-bounded finalization and claim paths.
- Surplus above the buffer can be invested, but recall paths must handle ERC4626 rounding, strategy losses, and forced withdrawal failure.
- Invariant tests should cover reserve target, invested surplus, recall amount, and user redemption liveness.
- Parallel exit paths must share the same reserve predicate. Instant withdrawals, priority queues, NFT exits, and normal queues should subtract each other's locked claims before treating liquidity as free.
- Admin rescue or surplus-withdrawal functions must prove the amount is above all withdrawal locks, low-watermark buffers, and claim reserves.
- Multi-asset redemption queues should subtract outstanding per-token debt from each token's quota or capacity before accepting new requests.
- Process multi-asset claims through an explicit cursor, id range, or max-count bound.
- Per-token pauses and fast-lane reserves are exit-liveness risks; document how they interact with normal queue claims.
- Instant RWA redemption buffers should cap redeemable shares by actual idle or yield liquidity, round redeemable capacity down, round required input up for exact payout, and fail closed on stale or below-minimum oracle prices.
- LST delayed exits should maintain aggregate pending-ticket amount and count, and claim paths should check reserve availability before payment.

## Source Evidence

- Renzo subtracts claim reserves from available withdrawal liquidity, computes withdrawal deficits from buffer and queue state, and routes deposits into deficits before delegating surplus assets.
- Renzo's instant withdrawal path blocks withdrawals when the buffer is insufficient and scales fees by remaining buffer capacity.
- Ether.fi excludes normal and priority withdrawal locks plus a low watermark before instant redemption, and tests queued exits through rebases and slashing.
- Ethena's surplus rescue design highlights that admin withdrawals must be limited to assets above user claims and buffer requirements.
- An Ondo audit-contest snapshot uses existing USDC first, redeems at least an external minimum lot when necessary, and verifies the external redemption by exact USDC balance delta.
- Bedrock uniBTC delayed redemption queues subtract per-token debts from quota before accepting requests, process claims through bounded cursor paths, and expose per-token pause and fast-lane reserve trade-offs.
- Superstate on-chain redemptions cap instant RWA redemptions by available idle or yield liquidity, use conservative rounding, and fail closed on stale or below-minimum oracle prices.
- Marinade delayed unstake tickets maintain aggregate pending balances and claim from reserve after maturity.

## Related Patterns

- [Async Deposit/Withdrawal](./pattern-async-deposit.md) - queue and claim mechanics
- [Vault Fairness Requirements](./req-vault-fairness.md) - exit liveness and cost attribution
- [Withdrawal Queue Starvation](../../ANTIPATTERNS.md#withdrawal-queue-starvation) - risk this mitigates
