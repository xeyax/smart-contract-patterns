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

## Trade-offs

**Pros:**
- New actions ship through registry additions without redeploying wallets or the executor
- Stateless action modules are reusable across every recipe and wallet
- Return-value piping enables multi-step flows like flash-loan, swap, repay in one transaction
- A timelocked registry gives users a review window before module changes take effect

**Cons:**
- Delegatecall into registry-resolved code runs with full wallet authority; one malicious or storage-clobbering module compromises the wallet outright
- Security collapses onto registry governance, so weak admin keys turn the registry into a universal backdoor for all users
- Parameter injection and typed return parsing are fragile plumbing that demands heavy audit attention
- Per-step slippage, receiver, approval-spender, and selector bounds must be enforced in every action; a single missing check undermines the whole recipe
- Delegatecall storage-layout compatibility permanently constrains how modules can be written

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
- LI.FI executor-style bridge and swap composition illustrates why multi-step recipes need per-step target, selector, approval, receiver, and slippage boundaries in [`src/Periphery/Executor.sol`](https://github.com/lifinance/contracts/blob/7aeb2419d52d6bf834bf2c47e54dd8ea470a57bd/src/Periphery/Executor.sol) and `src/Helpers/SwapperV2.sol`.

## Related Patterns

- [Timelocked Address Registry](../upgrades/pattern-timelocked-address-registry.md)
- [Wallet-Native Automation Auth Adapter](../access-control/pattern-wallet-native-automation-auth-adapter.md)
