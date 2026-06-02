# Read-Only Protocol Health Checker

> Package production and fork invariant checks into read-only contracts or scripts that return structured health results without mutating protocol state.

## Metadata

| Property | Value |
|----------|-------|
| Category | monitoring |
| Tags | monitoring, invariants, health-check, upgrade, fork-test |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Low |

## Use When

- A protocol has many deployed pools, strategies, managers, or upgradeable instances
- Operators need repeatable pre-upgrade and post-upgrade checks
- Invariants can be evaluated from public state without privileged writes
- Fork tests should share logic with production monitoring

## Avoid When

- Checks require mutating live protocol state
- A failed check cannot be mapped to a specific component or invariant
- The health checker has privileged permissions that could change behavior

## Trade-offs

**Pros:**
- Reuses invariant logic across tests, deployments, and monitoring
- Gives upgrade runbooks objective pass/fail gates
- Makes hidden cross-contract assumptions explicit

**Cons:**
- Read-only checks can miss behavior that depends on future transactions
- Large deployments may need pagination
- A stale checker can create false confidence after protocol changes

## How It Works

Expose bounded read-only checks that return structured results:

```solidity
struct CheckResult {
    bool ok;
    bytes32 checkId;
    address target;
    string message;
}

function checkPool(address pool) external view returns (CheckResult[] memory results) {
    results = new CheckResult[](3);
    results[0] = _checkAccounting(pool);
    results[1] = _checkPermissions(pool);
    results[2] = _checkWithdrawalManager(pool);
}
```

Deployment scripts and fork tests call the same checker before and after changes.

## Key Points

- Keep checks read-only and deterministic.
- Return machine-readable identifiers, not only revert strings.
- Cover accounting, permissions, dependency wiring, withdrawal liveness, and version state.
- Use pagination for large instance sets.
- Treat checker updates as part of protocol upgrades.
- For liquidators or keepers, expose read-only prechecks that return eligibility and required accounts before sending a state-changing transaction.

## Source Evidence

- Maple packages protocol health checker contracts and tests that evaluate pools, managers, withdrawal modules, permissions, strategies, and upgrade validation flows through read-only checks.
- Solana Labs Perpetuals exposes a read-only liquidation-state instruction and a liquidator client that uses it before submitting liquidation transactions in `/private/tmp/defillama-source/solana-labs_perpetuals/programs/perpetuals/src/instructions/get_liquidation_state.rs` and `/private/tmp/defillama-source/solana-labs_perpetuals/app/src/liquidator.ts`.

## Related Patterns

- [Version-Gated Upgrade Registry](../upgrades/pattern-version-gated-upgrade-registry.md)
- [Lending Accounting Freshness Requirements](../lending/req-lending-accounting-freshness.md)
- [State Machine Gaps](../../ANTIPATTERNS.md#state-machine-gaps)
