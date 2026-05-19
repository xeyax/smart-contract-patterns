# Mutually Exclusive Entity Protocol Allowlist

> Separate human or legal-entity eligibility from protocol-contract eligibility so one address cannot silently hold both identities.

## Metadata

| Property | Value |
|----------|-------|
| Category | access-control |
| Tags | access-control, allowlist, rwa, protocol-contract, entity |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Regulated tokens distinguish investor/entity eligibility from protocol-contract eligibility
- Protocol contracts need transfer privileges different from end users
- Compliance state is fund-specific or token-specific
- Reassigning an address between entities changes transfer rights

## Avoid When

- All allowed addresses have identical rights
- Protocol contracts do not need special eligibility semantics
- Code presence cannot be checked or is not meaningful for the chain
- Entity reassignment is expected to be frequent and operationally loose

## How It Works

Store entity and protocol eligibility separately and make the two roles mutually exclusive:

```solidity
function setEntityAddress(address account, bytes32 entityId) external onlyAdmin {
    require(!protocolAllowed[account], "protocol address");
    require(entityOf[account] == bytes32(0) || entityId == bytes32(0), "zero first");
    entityOf[account] = entityId;
}

function setProtocolAllowed(address account, bool allowed) external onlyAdmin {
    require(account.code.length != 0, "not contract");
    require(entityOf[account] == bytes32(0), "entity address");
    protocolAllowed[account] = allowed;
}
```

Transfer checks then decide whether the account is eligible as an entity member or as an approved protocol contract for the specific fund.

## Key Points

- Enforce mutual exclusion between entity and protocol-contract roles.
- Require code at protocol-contract addresses where the chain supports it.
- Force explicit zeroing before reassigning an address to another entity.
- Keep fund-specific eligibility separate from global address status.
- Emit events that include old and new entity or protocol state.
- Test entity-to-protocol, protocol-to-entity, reassignment, and no-code protocol cases.

## Source Evidence

- Superstate USTB allowlist logic distinguishes entity eligibility from protocol-contract eligibility, enforces mutual exclusion, requires protocol addresses to have code, and tests reassignment constraints.

## Related Patterns

- [Participant Permission Bitmap](./pattern-participant-permission-bitmap.md)
- [Permissioned Exit Custody](../../ANTIPATTERNS.md#permissioned-exit-custody)
