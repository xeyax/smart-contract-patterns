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

## Key Points

- Separate active membership from deposit and withdrawal preference.
- Gate removal on dust or zero delegated stake.
- Emit old and new role flags on every update.
- Monitor concentration and stuck delegated balances per operator.
- Test role toggles around pending deposits and withdrawals.

## Source Evidence

- Stader BNBx uses an operator registry with curated validator membership, separate preferred deposit and withdrawal operators, and dust-gated removal tests.

## Related Patterns

- [Operator-Routed Liquid Staking Share](./pattern-operator-routed-liquid-staking-share.md)
- [Unrestricted Admin](../../ANTIPATTERNS.md#unrestricted-admin)
