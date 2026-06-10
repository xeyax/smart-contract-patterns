# Deferred Status Check Frame

> Batch lending operations can defer account and vault status checks until the outer execution frame exits, then validate every touched account before state is released.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, batch, solvency, controller, deferred-checks |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Users need batch operations that temporarily move through an unsafe intermediate state
- Account, collateral, or vault checks are expensive but must still run before completion
- A controller or vault can declare that an account must be checked
- The set of deferred checks can be bounded tightly

## Avoid When

- The protocol cannot prove every deferred check is executed before frame exit
- The deferred account or vault set can grow without a hard cap
- Reentrancy can enter another frame and clear or bypass pending checks
- Intermediate unsafe state can be externally observed and exploited

## Trade-offs

**Pros:**
- Batches can pass through temporarily unsafe intermediate states (e.g. borrow-then-collateralize), enabling flows immediate checks would forbid.
- Each touched account is checked once at frame exit instead of after every inner call, amortizing expensive health checks across the batch.
- Hard-capped deferred sets keep the worst-case exit-validation gas bounded and predictable.
- Scoped forgiveness lets legitimately redundant checks be removed without weakening unrelated accounts' checks.

**Cons:**
- Correctness hinges on proving every touched account/vault lands in the deferred set and is checked before exit — a missed enqueue path is a direct solvency hole.
- Frame context (active account, spell, executor) is mutable global state; reentrancy into another frame or a callback mutating unrelated positions are first-class attack vectors.
- Forgiveness paths invert the safety default and must be tightly scoped, adding their own audit surface.
- Set caps create UX failure modes: complex batches touching too many accounts revert at the cap.
- The many variants (spell, wallet hook, credit-account adapter) each add bespoke context-cleanup and permission logic that must be individually verified.

## How It Works

The entrypoint opens an authenticated execution frame, lets inner calls enqueue account and vault checks, and then runs all queued checks before restoring the outer context:

```solidity
function batch(Call[] calldata calls) external {
    _enterDeferredFrame(msg.sender);

    for (uint256 i; i < calls.length; i++) {
        _dispatch(calls[i]);
    }

    _runDeferredAccountChecks();
    _runDeferredVaultChecks();
    _exitDeferredFrame();
}

function requireAccountCheck(address account) internal {
    if (_checksDeferred()) {
        deferredAccounts.add(account); // bounded set
    } else {
        _checkAccount(account);
    }
}
```

Validation must re-enforce the same invariants as the immediate path. For lending, that usually means one active controller per account, collateral support, vault health, and no stale risk state.

A spell-mediated variant stores the active position id and spell during the
outer frame, allows only that spell to call privileged bank actions, and checks
collateral value against borrow value after the spell returns. The temporary
position and spell context must be cleared only after the final health check
passes or the whole transaction reverts.

### Scoped Forgiveness Variant

Deferred frames sometimes need to remove a scheduled check after a later action
has made the check intentionally invalid or redundant. That forgiveness path must
be scoped: only the relevant account or calling vault can remove its own pending
check, and the frame must still enforce all remaining account and vault checks at
the outer boundary.

### Modular Wallet Hook Variant

Smart-wallet or safe modules can defer solvency checks until after a sequence of
module calls completes. The post-operation hook should receive the touched wallet
or account, re-run debt-manager health checks, and fail the whole frame if the
wallet is insolvent after the module action.

### Credit-Account Adapter Frame Variant

Credit-account protocols can batch adapter calls, token enables/disables, quota
changes, and collateral withdrawals inside one frame. The frame should scope each
action by permission bits, set a temporary active credit account only while the
adapter executes, clear it before exit, and run final collateral checks with the
right safe-price and forbidden-token rules when calls can offload or withdraw
collateral.

## Key Points

- Hard-cap the deferred account and vault sets.
- Treat the outer frame as the only place that can clear pending checks.
- Lock status-check execution against reentrancy.
- Restore caller/account context after checks, not before.
- Validate that every controller or vault touched during the frame appears in the deferred sets.
- Add tests where an account is unsafe mid-frame but safe at exit, and tests where a missing final check reverts.
- If the frame exposes a temporary executor, prove callbacks cannot use the active frame to mutate unrelated positions.
- If forgiveness exists, test that it cannot remove unrelated accounts or vaults and that reentrant status-check execution is locked.
- For modular wallets, bind the post-operation hook to the active wallet and debt manager; module execution must not be able to skip the final solvency hook.
- For credit-account adapter frames, test permission bits, active-account
  cleanup, forbidden-token checks, safe-price checks, and failure paths where an
  adapter tries to mutate an unrelated account.
- Open arbitrary-call batching only to authenticated borrowers and ensure the
  final exchange-rate or solvency guard cannot be bypassed by stale-price
  fallback behavior.

## Source Evidence

- Euler's Ethereum Vault Connector defers account and vault status checks during `call`, `controlCollateral`, and `batch` frames, caps internal check sets, restores context at outer-frame exit, and tests deferred scheduling followed by validation.
- Euler EVC exposes scoped `forgiveAccountStatusCheck` and `forgiveVaultStatusCheck` paths, caps deferred account and vault sets at 10, blocks status-check reentrancy, and restores execution context after the outer frame in [`src/EthereumVaultConnector.sol`](https://github.com/euler-xyz/ethereum-vault-connector/blob/b9d557a8ebcd3db1fbeef4aa60282aa4059a7bbf/src/EthereumVaultConnector.sol), `src/ExecutionContext.sol`, and `docs/whitepaper.md`.
- Alpha Homora V2 stores `POSITION_ID` and `SPELL` during `execute`, restricts bank actions to the active spell, checks collateral value against borrow value after spell execution, and clears the temporary context in [`contracts/HomoraBank.sol`](https://github.com/AlphaFinanceLab/alpha-homora-v2-contract/blob/f74fc460bd614ad15bbef57c88f6b470e5efd1fd/contracts/HomoraBank.sol).
- EtherFi Cash V3 safe modules run post-operation debt-manager checks through `EtherFiSafe`, `ModuleManager`, and `EtherFiHook` in [`src/safe/EtherFiSafe.sol`](https://github.com/etherfi-protocol/cash-v3/blob/e05bda2be27a6a606f3f1b8ff0d0791032fd0ff8/src/safe/EtherFiSafe.sol) and `src/hook/EtherFiHook.sol`.
- Gearbox V3 batches credit-account calls with permission-bit checks, temporary
  active-account context, adapter execution, and final collateral checks in
  [`contracts/credit/CreditFacadeV3.sol:440-486`](https://github.com/gearbox-protocol/core-v3/blob/b038597d9070d9fd18593a6ae9c3d28ca931bb73/contracts/credit/CreditFacadeV3.sol#L440-L486),
  [`contracts/credit/CreditFacadeV3.sol:492-650`](https://github.com/gearbox-protocol/core-v3/blob/b038597d9070d9fd18593a6ae9c3d28ca931bb73/contracts/credit/CreditFacadeV3.sol#L492-L650),
  and [`contracts/credit/CreditManagerV3.sol:512-591`](https://github.com/gearbox-protocol/core-v3/blob/b038597d9070d9fd18593a6ae9c3d28ca931bb73/contracts/credit/CreditManagerV3.sol#L512-L591).
- Abracadabra Cauldron V3 exposes open-call batching through `cook`, guarded by
  borrower context and final exchange-rate/solvency checks, in
  [`contracts/CauldronV3.sol:36-39`](https://github.com/abracadabra-money/magic-internet-money/blob/23266d17969a95e69199670cba9d0060bff33340/contracts/CauldronV3.sol#L36-L39),
  [`contracts/CauldronV3.sol:390-414`](https://github.com/abracadabra-money/magic-internet-money/blob/23266d17969a95e69199670cba9d0060bff33340/contracts/CauldronV3.sol#L390-L414),
  and [`contracts/CauldronV3.sol:422-493`](https://github.com/abracadabra-money/magic-internet-money/blob/23266d17969a95e69199670cba9d0060bff33340/contracts/CauldronV3.sol#L422-L493).

## Related Patterns

- [Comptroller Risk Gate](./pattern-comptroller-risk-gate.md)
- [Lending Accounting Freshness Requirements](./req-lending-accounting-freshness.md)
- [Unbounded Iteration](../../ANTIPATTERNS.md#unbounded-iteration)
