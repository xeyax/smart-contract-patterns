# Withdrawal Liquidity Buffer

> Reserve enough liquid assets for claims, route new inflows to queued withdrawal deficits first, and only deploy surplus capital.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, withdrawal, buffer, liquidity, queue, liveness |
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

For instant unstake pools, count incoming stake accounts as pending liabilities until the stake is deactivated and reclaimed into liquid reserves. Quote redeemable liquidity from `pool_reserves - incoming_stake` or an equivalent predicate, reject locked stake that cannot become reserve liquidity, and reconcile the recorded lamports when the stake account is reclaimed.

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
- Lending-market vault allocators should bound supply and withdrawal queues,
  validate queue edits, and keep forced-removal recovery paths so users can exit
  a market that governance has removed from normal allocation.
- For validator or nominator pools, block new stake deployment while withdrawal requests are pending, and expose a bounded public drain path so exits do not depend on one operator.
- Instant withdrawal buffers should subtract low-watermark liquidity before quoting redeemable capacity; the low watermark is not rescueable surplus.
- Instant unstake pools should track incoming stake as a liability until reclaimed, and utilization fees should be computed from post-unstake reserve liquidity.
- If LP mint or burn value includes flash-borrowed reserves, include the borrowed amount consistently in liquidity snapshots and enforce instruction-paired repayment.
- Transmuter or savings buffers should keep redemption liquidity out of redeployable strategy balances and route newly available underlying to pending claims before ordinary deployment.

## Source Evidence

- Renzo subtracts claim reserves from available withdrawal liquidity, computes withdrawal deficits from buffer and queue state, and routes deposits into deficits before delegating surplus assets.
- Renzo's instant withdrawal path blocks withdrawals when the buffer is insufficient and scales fees by remaining buffer capacity.
- Ether.fi excludes normal and priority withdrawal locks plus a low watermark before instant redemption, and tests queued exits through rebases and slashing.
- Ethena's surplus rescue design highlights that admin withdrawals must be limited to assets above user claims and buffer requirements.
- An Ondo audit-contest snapshot uses existing USDC first, redeems at least an external minimum lot when necessary, and verifies the external redemption by exact USDC balance delta.
- Bedrock uniBTC delayed redemption queues subtract per-token debts from quota before accepting requests, process claims through bounded cursor paths, and expose per-token pause and fast-lane reserve trade-offs.
- Superstate on-chain redemptions cap instant RWA redemptions by available idle or yield liquidity, use conservative rounding, and fail closed on stale or below-minimum oracle prices.
- Marinade delayed unstake tickets maintain aggregate pending balances and claim from reserve after maturity.
- Frax frxETH V2 represents LST exits as NFT redemption tickets with maturity, fee snapshot, liabilities, and full or partial ETH redemption paths in [`src/contracts/frxeth-redemption-queue-v2/FraxEtherRedemptionQueueCore.sol`](https://github.com/FraxFinance/frxETH-v2-public/blob/83dfe93b4a32b9ca0ab93d6e7c059fcd977320d4/src/contracts/frxeth-redemption-queue-v2/FraxEtherRedemptionQueueCore.sol) and `FraxEtherRedemptionQueueV2.sol`.
- SlowMist's Avalon USDa audit noted that saving-account redemption and interest distribution can leave claims underfunded if the contract lacks enough underlying tokens, a lower-confidence audit-source example for funded claim reserves.
- Satoshi Core can deploy CDP collateral into vaults while retaining local reserve percentages and recalling through priority adapters when withdrawal demand exceeds local liquidity in [`src/core/TroveManager.sol`](https://github.com/Satoshi-Protocol/satoshi-core/blob/7f5eddaed965904fde10ea1d40c4c4b3ea118ada/src/core/TroveManager.sol) and `src/vault/VaultManager.sol`.
- Kinetiq queues L1 staking operations, converts withdrawal amounts with withdrawal-favoring rounding, and processes pending L1 withdrawals before deposit and rebalance operations in [`src/StakingManager.sol`](https://github.com/code-423n4/2025-04-kinetiq/blob/a3913ca2b9d021df45a428e0185ee4f4f45509ae/src/StakingManager.sol).
- RAAC keeps a lending-pool liquidity buffer ratio, calls `_ensureLiquidity` before withdrawals, and rebalances through `_rebalanceLiquidity` when local liquidity and externally deployed yield positions diverge in [`contracts/core/pools/LendingPool/LendingPool.sol`](https://github.com/tinnohofficial/2025-02-raac/blob/dd5516a9b318b797f82015ee63170d9064514b16/contracts/core/pools/LendingPool/LendingPool.sol).
- TON Nominator Pool stores withdraw requests, lets anyone process bounded batches or single emergency requests, and rejects new stake while withdraws are pending in [`func/pool.fc`](https://github.com/ton-blockchain/nominator-pool/blob/2f35c36b5ad662f10fd7b01ef780c3f1949c399d/func/pool.fc), with queue limit and balance tests in `test/withdraw-requests-limit.js`, `withdraw-requests-balance.js`, and `new-stake-has-withdraws.js`.
- EtherFi beHYPE excludes a low watermark before instant withdrawals in [`src/WithdrawManager.sol`](https://github.com/etherfi-protocol/beHYPE/blob/06ee135254508fa3f0ab6b1bd8e80dc805884420/src/WithdrawManager.sol).
- Sanctum's unstake program records incoming stake lamports separately from SOL reserves, subtracts incoming stake when quoting instant unstake capacity, rejects locked stake, and reconciles reclaimed stake in [`programs/unstake/src/state/pool.rs`](https://github.com/igneous-labs/sanctum-unstake-program/blob/b6db89b0d39e8ff798171331dd6f8d120dbc9327/programs/unstake/src/state/pool.rs), `instructions/unstake_instructions/unstake_accounts.rs`, and `instructions/reclaim_stake_account.rs`.
- Sanctum's unstake fee curve charges more as reserves fall toward depletion, and tests exercise fee behavior at different reserve utilization levels in [`programs/unstake/src/state/fee.rs`](https://github.com/igneous-labs/sanctum-unstake-program/blob/b6db89b0d39e8ff798171331dd6f8d120dbc9327/programs/unstake/src/state/fee.rs) and `tests/test-unstake-integration.ts`.
- Sanctum's unstake LP accounting includes flash-borrowed reserve amounts consistently in add/remove liquidity snapshots while paired flash-loan instructions enforce repayment in [`programs/unstake/src/utils.rs`](https://github.com/igneous-labs/sanctum-unstake-program/blob/b6db89b0d39e8ff798171331dd6f8d120dbc9327/programs/unstake/src/utils.rs), `instructions/add_liquidity.rs`, `instructions/remove_liquidity.rs`, `instructions/take_flash_loan.rs`, and `instructions/repay_flash_loan.rs`.
- MetaMorpho bounds market supply and withdraw queues, validates queue removal,
  and documents forced market-removal recovery in [`src/libraries/ConstantsLib.sol:15`](https://github.com/morpho-org/metamorpho/blob/163eb2ae022629d4c35e598a668a30451af25f44/src/libraries/ConstantsLib.sol#L15),
  [`src/MetaMorpho.sol:308`](https://github.com/morpho-org/metamorpho/blob/163eb2ae022629d4c35e598a668a30451af25f44/src/MetaMorpho.sol#L308),
  and [`README.md:158`](https://github.com/morpho-org/metamorpho/blob/163eb2ae022629d4c35e598a668a30451af25f44/README.md#L158).
- Alchemix `TransmuterBuffer` separates redemption liquidity from active yield deployment in [`src/TransmuterBuffer.sol`](https://github.com/alchemix-finance/v2-foundry/blob/8915ef7b1714c16f9e260a4ef41c5f254d5b7f58/src/TransmuterBuffer.sol), with tests in [`test/TransmuterBuffer.spec.ts`](https://github.com/alchemix-finance/v2-foundry/blob/8915ef7b1714c16f9e260a4ef41c5f254d5b7f58/test/TransmuterBuffer.spec.ts).
- Origin Dollar withdrawal queues and vault buffer state track pending requests and available liquidity in [`contracts/contracts/vault/VaultStorage.sol`](https://github.com/originprotocol/origin-dollar/blob/cd7218c2b070a52470b2621c3ce0ce12378ba700/contracts/contracts/vault/VaultStorage.sol) and [`contracts/contracts/vault/VaultCore.sol`](https://github.com/originprotocol/origin-dollar/blob/cd7218c2b070a52470b2621c3ce0ce12378ba700/contracts/contracts/vault/VaultCore.sol).

## Related Patterns

- [Async Deposit/Withdrawal](./pattern-async-deposit.md) - queue and claim mechanics
- [Vault Fairness Requirements](./req-vault-fairness.md) - exit liveness and cost attribution
- [Withdrawal Queue Starvation](../../ANTIPATTERNS.md#withdrawal-queue-starvation) - risk this mitigates
