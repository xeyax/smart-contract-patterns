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
- Lido's Deposit Security Module gates beacon deposits with guardian attestations over chain/contract-bound block data, deposit root, staking module id, and nonce; execution rechecks the deposit root and module nonce and rejects duplicate or unsorted guardian signatures in `/private/tmp/defillama-source/lidofinance__core/contracts/0.8.9/DepositSecurityModule.sol`.

## Related Patterns

- [Operator-Routed Liquid Staking Share](./pattern-operator-routed-liquid-staking-share.md)
- [Stake Pool Epoch Accounting Freshness Requirements](./req-stake-pool-epoch-accounting-freshness.md)
- [Restaking Slashing Accounting Requirements](./req-restaking-slashing-accounting.md)
- [Unrestricted Admin](../../ANTIPATTERNS.md#unrestricted-admin)
