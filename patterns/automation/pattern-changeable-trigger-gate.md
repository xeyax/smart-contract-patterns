# Changeable Trigger Gate

> Require every strategy trigger to pass, then atomically update only the selected mutable trigger state during execution.

## Metadata

| Property | Value |
|----------|-------|
| Category | automation |
| Tags | automation, trigger, strategy, keeper, state |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Automated strategies depend on multiple trigger conditions
- Some triggers carry mutable subscription state such as next execution time
- Bots should not update trigger data unless execution succeeds
- Read-only trigger simulation should avoid reverting when possible

## Avoid When

- Trigger checks are subjective or off-chain only
- Mutable trigger state can be advanced without executing the strategy
- A single trigger controls unrelated strategies
- Trigger state updates are not hash-bound to the subscription

## Trade-offs

**Pros:**
- Mutable trigger state advances only on successful execution, so failed runs leave the subscription re-executable
- The explicit changed-trigger index stops bots from silently advancing unrelated trigger state
- Non-reverting simulation views make off-chain bot discovery cheap
- All-triggers-must-pass keeps multi-condition semantics easy to reason about

**Cons:**
- Every execution iterates all triggers, so gas grows linearly with trigger count
- Only one mutable trigger updates per execution; strategies with several mutable triggers need careful extra design
- Trigger implementations must split view-style simulation from stateful updates, duplicating logic that can drift
- Wrong or attacker-chosen changed-trigger indexes are a subtle bug class requiring dedicated tests
- Bots bear simulation cost and can race each other for the same executable subscription

## How It Works

Evaluate all triggers first, execute the recipe, then update the chosen mutable trigger data in the same transaction:

```solidity
function execute(Strategy calldata strategy, uint256 changedTrigger) external {
    for (uint256 i; i < strategy.triggers.length; i++) {
        require(strategy.triggers[i].isTriggered(), "trigger");
    }
    _executeActions(strategy.actions);
    strategy.triggers[changedTrigger].updateSubData();
}
```

The mutable trigger index is part of execution context, so bots cannot silently advance unrelated trigger state.

## Key Points

- Require all triggers to pass before action execution.
- Update mutable trigger state only after successful execution.
- Bind the changed trigger to the subscribed strategy.
- Provide non-reverting simulation views for bot discovery.
- Test stale trigger data, wrong changed-trigger index, and failed-action rollback.

## Source Evidence

- Defi Saver V3 evaluates strategy triggers, executes actions, and updates selected changeable trigger subscription data atomically.

## Related Patterns

- [Hash-Anchored Strategy Subscription](./pattern-hash-anchored-strategy-subscription.md)
- [Registry-Routed Wallet Recipes](./pattern-registry-routed-wallet-recipes.md)
