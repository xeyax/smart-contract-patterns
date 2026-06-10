# Curated Validator Operator Registry

> Maintain an operator registry that separates validator membership from preferred deposit and withdrawal routing.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, liquid-staking, validator, operator-registry |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Liquid staking depends on a curated validator set
- Deposit and withdrawal operations need different preferred operators
- Removing an operator must account for delegated dust or pending exits
- Monitoring should reconstruct active and preferred operator sets

## Avoid When

- Any validator should be accepted permissionlessly
- Operator changes are too frequent for governance or multisig review
- The staking protocol cannot detect remaining delegated balances
- Routing preference is purely off-chain

## Trade-offs

**Pros:**
- Role-specific preference flags let deposit and withdrawal routing change without touching membership, narrowing each governance action.
- Dust-gated removal prevents stranding delegated stake on a deactivated operator.
- On-chain role flags and key-state counters give monitoring a reconstructible operator picture instead of off-chain spreadsheets.
- Snapshot-tied limit increases and global pubkey uniqueness close key-swap and duplicate-key attack paths.

**Cons:**
- Permissioned curation concentrates trust in governance/multisig; a captured curator controls validator selection for all depositors.
- Per-operator state (uploaded, audited, funded, exit counters, residuals) is a wide accounting surface that must stay consistent with the staking layer or removals and limits break.
- Removal gated on dust and pending exits can block legitimate offboarding for long unbonding periods, leaving misbehaving operators technically active.
- Every membership/role/limit change is a governance round-trip — operational latency that a permissionless set avoids.
- Capped or allocation-driven loops bound gas but add keeper dependence and vector-validation logic (sorted, nonzero, fundable-key checks) that must be tested per release.

## How It Works

Track operator membership and role-specific preferences:

```solidity
struct Operator {
    bool active;
    bool preferredForDeposit;
    bool preferredForWithdrawal;
}

function removeOperator(address operator) external onlyGovernance {
    require(delegatedStake[operator] <= removalDustLimit, "stake remains");
    operators[operator].active = false;
}
```

Deposit and withdrawal flows then check the relevant role, not only generic membership.

### Allocation Vector Variant

Some staking systems use keeper-provided allocation vectors instead of preferred operator flags. In that model, the vector should be sorted, nonzero, bounded by committed funds, and checked against each operator's remaining fundable keys before deposits execute.

## Key Points

- Separate active membership from deposit and withdrawal preference.
- Gate removal on dust or zero delegated stake.
- Emit old and new role flags on every update.
- Monitor concentration and stuck delegated balances per operator.
- Test role toggles around pending deposits and withdrawals.
- Distinguish uploaded keys, audited/fundable limit, funded count, requested exits, stopped exits, and active status.
- Tie operator limit increases to an audited key snapshot; reject or skip increases if keys changed after the snapshot.
- Make pubkeys globally single-use across delegators or operators.
- Gate operator or delegator removal on residual balances, pending unstaking, and negligible dust.
- Keep oracle or deposit-critical loops capped or allocation-driven.

## Source Evidence

- Stader BNBx uses an operator registry with curated validator membership, separate preferred deposit and withdrawal operators, and dust-gated removal tests.
- Liquid Collective tracks uploaded, audited, funded, requested-exit, stopped-exit, and active operator state, validates sorted allocation vectors, and ties fundable limits to key snapshots.
- Kelp enforces pubkey uniqueness across node delegators and gates delegator removal on queue size, balances, and residue checks.
- Lido's Deposit Security Module gates beacon deposits with guardian attestations over chain/contract-bound block data, deposit root, staking module id, and nonce; execution rechecks the deposit root and module nonce and rejects duplicate or unsorted guardian signatures in [`contracts/0.8.9/DepositSecurityModule.sol`](https://github.com/lidofinance/core/blob/c1250690f0b37202464cd4fb68e64ad6720328a4/contracts/0.8.9/DepositSecurityModule.sol).

## Related Patterns

- [Operator-Routed Liquid Staking Share](./pattern-operator-routed-liquid-staking-share.md)
- [Stake Pool Epoch Accounting Freshness Requirements](./req-stake-pool-epoch-accounting-freshness.md)
- [Restaking Slashing Accounting Requirements](./req-restaking-slashing-accounting.md)
- [Unrestricted Admin](../../ANTIPATTERNS.md#unrestricted-admin)
