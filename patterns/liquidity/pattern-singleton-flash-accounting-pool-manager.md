# Singleton Flash Accounting Pool Manager

> Keep many AMM pools in one manager and settle all per-currency deltas to zero at the end of an unlocked operation.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, singleton, flash-accounting, transient-storage, settlement |
| Complexity | High |
| Gas Efficiency | High |
| Audit Risk | High |

## Use When

- Many pools share the same execution environment and benefit from lower transfer overhead
- Pool identity is keyed by immutable parameters
- Operations can be wrapped in a transaction-scoped lock or unlock frame
- The protocol can enforce that every currency delta settles before the frame exits

## Avoid When

- Independent pool custody isolation is a hard requirement
- Hook or router code can leave unsettled deltas
- Market state is not keyed strongly enough to prevent cross-pool accounting bleed

## Trade-offs

**Pros:**
- Multi-hop routes net deltas inside one frame, eliminating per-pool token transfers and cutting swap gas substantially.
- One end-of-unlock zero-delta check enforces solvency for every pool, hook, and router action in the frame.
- Singleton deployment means one audited codebase and no per-pool deployment cost or bytecode drift.
- Immutable pool-id keying prevents cross-pool state bleed without per-pool custody contracts.

**Cons:**
- All pool funds share one contract, so a single manager bug is a protocol-wide loss; custody isolation is structurally unavailable.
- The unlock-callback model forces integrators through a callback frame — direct EOA interaction is impossible and router/periphery code becomes mandatory.
- Delta bookkeeping correctness spans sync, settle, fee collection, and reserve accounting; subtle interactions (e.g., donation-credited settlement) are easy to get wrong and must be capped explicitly.
- Transient-storage locking ties the design to specific EVM features and complicates porting or formal analysis.
- Hooks and routers that revert or leave nonzero deltas abort the whole frame, so one bad leg fails an entire multi-pool operation.

## How It Works

Users call `unlock`, perform swaps, liquidity changes, takes, settles, mints, or burns through the manager, then the manager verifies that no nonzero deltas remain:

```solidity
function unlock(bytes calldata data) external returns (bytes memory result) {
    require(!locked, "already unlocked");
    locked = false;
    result = IUnlockCallback(msg.sender).unlockCallback(data);
    require(nonzeroDeltaCount == 0, "currency not settled");
    locked = true;
}

function _accountDelta(address account, Currency currency, int256 delta) internal {
    int256 beforeDelta = currencyDelta[account][currency];
    int256 afterDelta = beforeDelta + delta;
    _updateNonzeroDeltaCount(beforeDelta, afterDelta);
    currencyDelta[account][currency] = afterDelta;
}
```

## Key Points

- Key pool state by immutable pool id, not by mutable caller assumptions.
- If the singleton holds balances for multiple registered applications, key reserves and deltas by app as well as currency.
- Count every account-currency delta that becomes nonzero and returns to zero.
- Require end-of-unlock solvency before state exits the operation frame.
- Make hooks and routers settle through the same delta ledger.
- When settlement credits from observed token balances, cap the credited amount
  by the caller-supplied settlement amount so donations cannot pay unrelated
  debt.
- Treat sync, settle, fee collection, and reserve accounting as part of the same invariant surface.
- Treat this as a narrow exception to shared-pool risk, justified only by keyed state and delta invariants.

## Source Evidence

- Uniswap V4's pool manager stores all pools in a singleton, exposes unlock-scoped flash accounting, and requires all nonzero currency deltas to clear before the unlock completes.
- PancakeSwap Infinity Core adds a shared vault variant with registered apps, app balances, transient locking, settlement guards, and unsettled-delta accounting in [`src/Vault.sol`](https://github.com/pancakeswap/infinity-core/blob/7c04695faeab8b06570cf6c277d9a9717136fb26/src/Vault.sol) and `src/libraries/SettlementGuard.sol`.
- Balancer V3 uses vault-scoped unlock frames and transient token deltas that
  must settle to zero before exit, with settlement credit limited by amount hints
  in [`pkg/vault/contracts/Vault.sol:82-163`](https://github.com/balancer/balancer-v3-monorepo/blob/0a5890a8c5d79865498d75cdc6ecdc75cf8d297d/pkg/vault/contracts/Vault.sol#L82-L163)
  and [`pkg/vault/contracts/VaultCommon.sol:72-120`](https://github.com/balancer/balancer-v3-monorepo/blob/0a5890a8c5d79865498d75cdc6ecdc75cf8d297d/pkg/vault/contracts/VaultCommon.sol#L72-L120).

## Related Patterns

- [Net Delta Settlement Invariants](./req-net-delta-settlement-invariants.md)
- [Verified Callback Settlement](./pattern-verified-callback-settlement.md)
- [Shared Pool Sink](../../ANTIPATTERNS.md#shared-pool-sink)
