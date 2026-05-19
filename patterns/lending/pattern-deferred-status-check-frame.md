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

## Source Evidence

- Euler's Ethereum Vault Connector defers account and vault status checks during `call`, `controlCollateral`, and `batch` frames, caps internal check sets, restores context at outer-frame exit, and tests deferred scheduling followed by validation.
- Euler EVC exposes scoped `forgiveAccountStatusCheck` and `forgiveVaultStatusCheck` paths, caps deferred account and vault sets at 10, blocks status-check reentrancy, and restores execution context after the outer frame in `/private/tmp/defillama-source/euler-xyz__ethereum-vault-connector/src/EthereumVaultConnector.sol`, `src/ExecutionContext.sol`, and `docs/whitepaper.md`.
- Alpha Homora V2 stores `POSITION_ID` and `SPELL` during `execute`, restricts bank actions to the active spell, checks collateral value against borrow value after spell execution, and clears the temporary context in `/private/tmp/defillama-source/AlphaFinanceLab__alpha-homora-v2-contract/contracts/HomoraBank.sol`.
- EtherFi Cash V3 safe modules run post-operation debt-manager checks through `EtherFiSafe`, `ModuleManager`, and `EtherFiHook` in `/private/tmp/defillama-source/etherfi-protocol_cash-v3/src/safe/EtherFiSafe.sol` and `src/hook/EtherFiHook.sol`.

## Related Patterns

- [Comptroller Risk Gate](./pattern-comptroller-risk-gate.md)
- [Lending Accounting Freshness Requirements](./req-lending-accounting-freshness.md)
- [Unbounded Iteration](../../ANTIPATTERNS.md#unbounded-iteration)
