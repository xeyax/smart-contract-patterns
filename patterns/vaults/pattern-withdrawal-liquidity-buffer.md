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

## Source Evidence

- Renzo subtracts claim reserves from available withdrawal liquidity, computes withdrawal deficits from buffer and queue state, and routes deposits into deficits before delegating surplus assets.
- Renzo's instant withdrawal path blocks withdrawals when the buffer is insufficient and scales fees by remaining buffer capacity.
- Ether.fi excludes normal and priority withdrawal locks plus a low watermark before instant redemption, and tests queued exits through rebases and slashing.
- Ethena's surplus rescue design highlights that admin withdrawals must be limited to assets above user claims and buffer requirements.

## Related Patterns

- [Async Deposit/Withdrawal](./pattern-async-deposit.md) - queue and claim mechanics
- [Vault Fairness Requirements](./req-vault-fairness.md) - exit liveness and cost attribution
- [Withdrawal Queue Starvation](../../ANTIPATTERNS.md#withdrawal-queue-starvation) - risk this mitigates
