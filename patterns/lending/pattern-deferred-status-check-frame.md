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

## Key Points

- Hard-cap the deferred account and vault sets.
- Treat the outer frame as the only place that can clear pending checks.
- Lock status-check execution against reentrancy.
- Restore caller/account context after checks, not before.
- Validate that every controller or vault touched during the frame appears in the deferred sets.
- Add tests where an account is unsafe mid-frame but safe at exit, and tests where a missing final check reverts.

## Source Evidence

- Euler's Ethereum Vault Connector defers account and vault status checks during `call`, `controlCollateral`, and `batch` frames, caps internal check sets, restores context at outer-frame exit, and tests deferred scheduling followed by validation.

## Related Patterns

- [Comptroller Risk Gate](./pattern-comptroller-risk-gate.md)
- [Lending Accounting Freshness Requirements](./req-lending-accounting-freshness.md)
- [Unbounded Iteration](../../ANTIPATTERNS.md#unbounded-iteration)
