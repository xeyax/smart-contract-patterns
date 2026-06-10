# Position-Scoped Manager Receiver

> Delegate position management with separate add/remove privileges and explicit receiver rules for value leaving the position.

## Metadata

| Property | Value |
|----------|-------|
| Category | access-control |
| Tags | delegation, position, receiver, manager, cdp |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A user-owned position can be managed by another account or automation service
- Some delegated actions add collateral or repay debt, while others withdraw value
- The protocol needs finer control than a single all-powerful manager role
- Removed collateral or surplus can be routed to different recipients

## Avoid When

- Delegation is all-or-nothing by design and funds never leave to a manager-chosen receiver
- Receiver semantics cannot be enforced on-chain
- Managers can mutate delegation state while executing privileged actions

## Trade-offs

**Pros:**
- Separates risk-reducing delegation from value-removing delegation
- Makes receiver trust assumptions explicit
- Lets users automate low-risk maintenance without granting withdrawal power

**Cons:**
- More delegation states to test and explain
- Receiver routing mistakes can still lose funds
- Integrators must track which manager class is needed for each action

## How It Works

The position owner grants separate privileges for adding and removing value.
Removal paths verify both manager authority and receiver constraints before
moving collateral, surplus, or redemption proceeds.

```solidity
function withdrawCollateral(uint256 positionId, uint256 amount, address receiver) external {
    address owner = ownerOf(positionId);
    if (msg.sender != owner) {
        require(removeManager[positionId][msg.sender], "not remove manager");
        require(_receiverAllowed(positionId, msg.sender, receiver), "bad receiver");
    }

    _withdraw(positionId, amount, receiver);
}
```

## Implementation

- Split add-only, adjust, remove, and batch-manager permissions where risk differs.
- Bind receivers to owner, manager, or an explicit allowlist.
- Emit events for manager and receiver changes.
- Prevent a manager from broadening its own authority during execution.
- Test unauthorized receiver changes, add-only manager withdrawals, and manager revocation.

## Source Evidence

- Liquity V2/Bold defines manager and receiver delegation in [`contracts/src/AddRemoveManagers.sol`](https://github.com/liquity/bold/blob/3fcaf602eb36541dd298c73710e067dcad42d8ae/contracts/src/AddRemoveManagers.sol).
- Bold borrower operations enforce manager checks and batch-manager paths in [`contracts/src/BorrowerOperations.sol`](https://github.com/liquity/bold/blob/3fcaf602eb36541dd298c73710e067dcad42d8ae/contracts/src/BorrowerOperations.sol).
- Bold tests include `borrowerOperationsOnBehalfTroveManagament.t.sol`.

## Real-World Examples

- Liquity V2/Bold separates position-management delegation and receiver routing for borrower troves.

## Related Patterns

- [Selector-Scoped Authority](./pattern-selector-scoped-authority.md)
- [Participant Permission Bitmap](./pattern-participant-permission-bitmap.md)
- [Account Role Confusion](../../ANTIPATTERNS.md#account-role-confusion)

## References

- Liquity V2/Bold add/remove manager contracts.
