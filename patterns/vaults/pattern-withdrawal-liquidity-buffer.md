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
- NFT redemption tickets should snapshot maturity, fee, liability, and beneficiary information, and partial redemption should reduce the ticket's remaining liability before paying out.
- Principal-plus-interest claim paths need funded reserves or enforced liquidity predicates; operator top-up cadence is monitoring, not trust-minimized withdrawal liveness.
- When lending collateral is deployed into yield vaults, keep a local reserve percentage and recall from priority adapters before withdrawals consume accounting balances the protocol cannot settle.
- If an L1 or external staking queue has both deposit and withdrawal operations pending, process withdrawal operations before new deposit or rebalance operations consume liquid capacity.
- Lending pools that deploy idle liquidity into yield adapters need a target buffer ratio, a recall path, and tests proving withdrawals cannot spend accounting balances that remain externally deployed.
- For validator or nominator pools, block new stake deployment while withdrawal requests are pending, and expose a bounded public drain path so exits do not depend on one operator.
- Instant withdrawal buffers should subtract low-watermark liquidity before quoting redeemable capacity; the low watermark is not rescueable surplus.

## Source Evidence

- Renzo subtracts claim reserves from available withdrawal liquidity, computes withdrawal deficits from buffer and queue state, and routes deposits into deficits before delegating surplus assets.
- Renzo's instant withdrawal path blocks withdrawals when the buffer is insufficient and scales fees by remaining buffer capacity.
- Ether.fi excludes normal and priority withdrawal locks plus a low watermark before instant redemption, and tests queued exits through rebases and slashing.
- Ethena's surplus rescue design highlights that admin withdrawals must be limited to assets above user claims and buffer requirements.
- An Ondo audit-contest snapshot uses existing USDC first, redeems at least an external minimum lot when necessary, and verifies the external redemption by exact USDC balance delta.
- Bedrock uniBTC delayed redemption queues subtract per-token debts from quota before accepting requests, process claims through bounded cursor paths, and expose per-token pause and fast-lane reserve trade-offs.
- Superstate on-chain redemptions cap instant RWA redemptions by available idle or yield liquidity, use conservative rounding, and fail closed on stale or below-minimum oracle prices.
- Marinade delayed unstake tickets maintain aggregate pending balances and claim from reserve after maturity.
- Frax frxETH V2 represents LST exits as NFT redemption tickets with maturity, fee snapshot, liabilities, and full or partial ETH redemption paths in `/private/tmp/defillama-source/FraxFinance__frxETH-v2-public/src/contracts/frxeth-redemption-queue-v2/FraxEtherRedemptionQueueCore.sol` and `FraxEtherRedemptionQueueV2.sol`.
- SlowMist's Avalon USDa audit noted that saving-account redemption and interest distribution can leave claims underfunded if the contract lacks enough underlying tokens, a lower-confidence audit-source example for funded claim reserves.
- Satoshi Core can deploy CDP collateral into vaults while retaining local reserve percentages and recalling through priority adapters when withdrawal demand exceeds local liquidity in `/private/tmp/defillama-source/Satoshi-Protocol__satoshi-core/src/core/TroveManager.sol` and `src/vault/VaultManager.sol`.
- Kinetiq queues L1 staking operations, converts withdrawal amounts with withdrawal-favoring rounding, and processes pending L1 withdrawals before deposit and rebalance operations in `/private/tmp/defillama-source/code-423n4__2025-04-kinetiq/src/StakingManager.sol`.
- RAAC keeps a lending-pool liquidity buffer ratio, calls `_ensureLiquidity` before withdrawals, and rebalances through `_rebalanceLiquidity` when local liquidity and externally deployed yield positions diverge in `/private/tmp/defillama-source/ryzen-xp__2025-02-raac/contracts/core/pools/LendingPool/LendingPool.sol`.
- TON Nominator Pool stores withdraw requests, lets anyone process bounded batches or single emergency requests, and rejects new stake while withdraws are pending in `/private/tmp/defillama-source/ton-blockchain__nominator-pool/func/pool.fc`, with queue limit and balance tests in `test/withdraw-requests-limit.js`, `withdraw-requests-balance.js`, and `new-stake-has-withdraws.js`.
- EtherFi beHYPE excludes a low watermark before instant withdrawals in `/private/tmp/defillama-source/etherfi-protocol_beHYPE/src/WithdrawManager.sol`.

## Related Patterns

- [Async Deposit/Withdrawal](./pattern-async-deposit.md) - queue and claim mechanics
- [Vault Fairness Requirements](./req-vault-fairness.md) - exit liveness and cost attribution
- [Withdrawal Queue Starvation](../../ANTIPATTERNS.md#withdrawal-queue-starvation) - risk this mitigates
