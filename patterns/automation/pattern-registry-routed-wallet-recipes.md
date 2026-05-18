# Registry-Routed Wallet Recipes

> Execute user-wallet recipes by resolving stateless action modules from a registry and piping typed outputs between steps.

## Metadata

| Property | Value |
|----------|-------|
| Category | automation |
| Tags | automation, wallet, recipe, registry, delegatecall |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Users execute multi-step DeFi operations through their own wallet or proxy
- Action modules can be stateless and reusable
- A registry can approve action IDs and implementation addresses
- Later steps need outputs from earlier steps

## Avoid When

- Actions need incompatible storage layouts under delegatecall
- The registry can be changed instantly or by weak admin keys
- Recipes can call arbitrary unregistered targets
- User slippage and receiver bounds are not enforced at the action layer

## How It Works

The executor resolves each action ID through a registry and executes it in wallet context:

```solidity
for (uint256 i; i < recipe.actions.length; i++) {
    address action = registry.getAddr(recipe.actions[i].id);
    bytes memory callData = _injectParams(recipe.actions[i].data, returnValues);
    bytes memory result = wallet.delegatecallAction(action, callData);
    returnValues[i] = _parseReturn(result);
}
```

The registry controls which modules are valid; the recipe controls sequence and parameter piping.

## Key Points

- Resolve action addresses by ID from a timelocked registry.
- Keep action modules stateless or storage-layout compatible with wallet execution.
- Validate injected parameters and typed return values.
- Enforce action-level slippage, receiver, deadline, and approval bounds.
- Test delegatecall context, registry replacement, and parameter piping failures.

## Source Evidence

- Defi Saver V3 executes recipes through registry-resolved action modules in user-wallet context and supports return-value/sub-parameter piping between actions.

## Related Patterns

- [Timelocked Address Registry](../upgrades/pattern-timelocked-address-registry.md)
- [Wallet-Native Automation Auth Adapter](../access-control/pattern-wallet-native-automation-auth-adapter.md)
