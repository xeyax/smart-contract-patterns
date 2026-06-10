# Grace-Period Keeper Bounties

> Convert overdue operator duties into permissionless maintenance after a grace period and pay a bounded bounty for completion.

## Metadata

| Property | Value |
|----------|-------|
| Category | automation |
| Tags | automation, keeper, bounty, validator, liveness, grace-period |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- A privileged operator or validator has recurring objective duties
- Operator disappearance can block exits, staking recovery, or state updates
- Third parties can safely determine when the duty is overdue
- A bounded bounty is needed to make public recovery economical

## Avoid When

- The action requires subjective judgment or private information
- Anyone can grief the protocol by racing the operator before the deadline
- The bounty can exceed the value preserved by the maintenance action
- The maintenance action cannot be made idempotent

## Trade-offs

**Pros:**
- Preserves liveness when the primary operator disappears
- Keeps the normal path cheap and permissioned before the grace period
- Gives keepers a clear economic reason to perform recovery

**Cons:**
- Bounty sizing becomes a protocol parameter
- The overdue predicate must be exact and testable
- Public execution can expose edge cases hidden from the operator-only path

## How It Works

The protocol tracks the expected deadline for an operator duty. Before the grace
period expires, only the operator can perform it. After the deadline, anyone can
perform the same objective transition and receive a capped bounty.

```solidity
function recoverStake(uint256 validatorId) external {
    Duty storage d = duties[validatorId];

    if (block.timestamp < d.deadline + gracePeriod) {
        require(msg.sender == d.operator, "operator only");
    }

    require(!d.completed, "done");
    d.completed = true;

    _recoverStake(validatorId);

    if (msg.sender != d.operator) {
        _payBounty(msg.sender, recoveryBounty);
    }
}
```

## Implementation

- Store the duty state, responsible operator, deadline, and completion marker.
- Make the public path available only after a clear grace period.
- Pay the bounty after state is marked complete.
- Bound the bounty and make it independent of caller-supplied values.
- Test operator path, early public rejection, late public success, duplicate calls, and bounty exhaustion.

## Source Evidence

- TON liquid staking allows overdue validator duties such as stake recovery, validator-hash updates, and unused-loan returns to become publicly executable with bounty mechanics in [`contracts/controller.func`](https://github.com/ton-blockchain/liquid-staking-contract/blob/1f4e9badbed52a4cf80cc58e4bb36ed375c6c8e7/contracts/controller.func).
- TON controller tests cover the delayed public recovery and update paths in [`tests/Controller.spec.ts`](https://github.com/ton-blockchain/liquid-staking-contract/blob/1f4e9badbed52a4cf80cc58e4bb36ed375c6c8e7/tests/Controller.spec.ts).
- TON Nominator Pool has older corroborating public maintenance paths in [`func/pool.fc`](https://github.com/ton-blockchain/nominator-pool/blob/2f35c36b5ad662f10fd7b01ef780c3f1949c399d/func/pool.fc).

## Real-World Examples

- TON liquid staking - overdue validator maintenance with permissionless bounty recovery.

## Related Patterns

- [Cranked Validator Set Maintenance](./pattern-cranked-validator-set-maintenance.md)
- [Operation Cadence Liveness Agent](../monitoring/pattern-operation-cadence-liveness-agent.md)
- [Withdrawal Liquidity Buffer](../vaults/pattern-withdrawal-liquidity-buffer.md)

## References

- See Source Evidence.
