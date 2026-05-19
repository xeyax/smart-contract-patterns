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
- If a recipe performs swaps or bridge calls, require target-selector allowlists and exact approval spenders for every external call in the recipe.
- Test delegatecall context, registry replacement, and parameter piping failures.

## Source Evidence

- Defi Saver V3 executes recipes through registry-resolved action modules in user-wallet context and supports return-value/sub-parameter piping between actions.
- LI.FI executor-style bridge and swap composition illustrates why multi-step recipes need per-step target, selector, approval, receiver, and slippage boundaries in `/private/tmp/defillama-source/lifinance__contracts/src/Periphery/Executor.sol` and `src/Helpers/SwapperV2.sol`.

## Related Patterns

- [Timelocked Address Registry](../upgrades/pattern-timelocked-address-registry.md)
- [Wallet-Native Automation Auth Adapter](../access-control/pattern-wallet-native-automation-auth-adapter.md)
