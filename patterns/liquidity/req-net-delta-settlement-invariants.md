# Net Delta Settlement Invariants

> Requirements for protocols that defer token movement into signed internal deltas and settle them at the end of an operation frame.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | settlement, flash-accounting, deltas, invariant, transient-storage |
| Type | Requirement |

## R1: Operation Frame Bounds All Deltas

**Every deferred debit and credit must be created inside a lock or unlock frame that cannot exit with unsettled deltas.**

### What This Means

- External entry points cannot call delta-creating operations while the manager is in the wrong lock state.
- The final frame check fails if any account-currency delta remains nonzero.
- Token-scoped transient deltas must clear before the unlock frame exits, even
  when the callback executes arbitrary router or hook logic.
- Tests cover nested calls, early reverts, and callback failures.

## R2: Nonzero Delta Count Matches Delta Storage

**The count of nonzero deltas must change exactly when a delta crosses zero.**

### What This Means

- Zero-to-nonzero increments the count.
- Nonzero-to-zero decrements the count.
- Nonzero-to-nonzero and zero-to-zero do not change the count.

## R3: Token Settlement Uses Fresh Synced Balances

**ERC20 settlement that relies on balance deltas must sync the expected reserve before accepting a transfer-derived settlement.**

### What This Means

- Native asset settlement and ERC20 settlement have distinct paths.
- ERC20 `settle` cannot credit stale donations or unrelated balance changes.
- If `settle` accepts an amount hint, credit at most the hinted amount so
  pre-existing token donations cannot satisfy the caller's debt.
- Dust clearing is exact and cannot erase meaningful debt.

## R4: Shared Vault Reserves Are App-Scoped

**When multiple apps or pools share one vault, each reserve and delta must be keyed to the app or pool that owns it.**

### What This Means

- A settlement for one app cannot consume another app's reserves.
- Fee collection, sync, settle, and take operations preserve app-scoped accounting.
- Invariants cover registered and unregistered apps separately.

## Verification Checklist

| Requirement | Question |
|-------------|----------|
| R1 | Can any callback or hook return while deltas remain nonzero? |
| R2 | Does fuzzing cover every zero-crossing delta transition? |
| R3 | Are sync, settle, take, clear, mint, and burn tested for stale balances? |
| R4 | Can one registered app settle or withdraw another app's reserve? |

## Source Evidence

- Uniswap V4 tracks currency deltas and nonzero-delta count during unlocked operations, and its settlement tests cover synced ERC20 balances, native settlement, dust clearing, and failed unlocks with unsettled deltas.
- PancakeSwap Infinity Core tests app-scoped shared vault settlement and invariants in [`test/vault/Vault.t.sol`](https://github.com/pancakeswap/infinity-core/blob/7c04695faeab8b06570cf6c277d9a9717136fb26/test/vault/Vault.t.sol) and `test/vault/VaultInvariant.t.sol`.
- Balancer V3 unlocks transient accounting through the vault, tracks
  token-scoped deltas that must all return to zero, and caps settlement credit
  by the caller's amount hint in [`pkg/vault/contracts/Vault.sol:82-163`](https://github.com/balancer/balancer-v3-monorepo/blob/0a5890a8c5d79865498d75cdc6ecdc75cf8d297d/pkg/vault/contracts/Vault.sol#L82-L163)
  and [`pkg/vault/contracts/VaultCommon.sol:72-120`](https://github.com/balancer/balancer-v3-monorepo/blob/0a5890a8c5d79865498d75cdc6ecdc75cf8d297d/pkg/vault/contracts/VaultCommon.sol#L72-L120).

## Related Patterns

- [Singleton Flash Accounting Pool Manager](./pattern-singleton-flash-accounting-pool-manager.md)
- [Balance Delta Transfer Accounting](../token-integration/pattern-balance-delta-transfer-accounting.md)
- [Hook/Callback Trust](../../ANTIPATTERNS.md#hookcallback-trust)
