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
- Treat sync, settle, fee collection, and reserve accounting as part of the same invariant surface.
- Treat this as a narrow exception to shared-pool risk, justified only by keyed state and delta invariants.

## Source Evidence

- Uniswap V4's pool manager stores all pools in a singleton, exposes unlock-scoped flash accounting, and requires all nonzero currency deltas to clear before the unlock completes.
- PancakeSwap Infinity Core adds a shared vault variant with registered apps, app balances, transient locking, settlement guards, and unsettled-delta accounting in `/private/tmp/defillama-source/pancakeswap__infinity-core/src/Vault.sol` and `src/libraries/SettlementGuard.sol`.

## Related Patterns

- [Net Delta Settlement Invariants](./req-net-delta-settlement-invariants.md)
- [Verified Callback Settlement](./pattern-verified-callback-settlement.md)
- [Shared Pool Sink](../../ANTIPATTERNS.md#shared-pool-sink)
