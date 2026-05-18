# Wallet-Native Automation Auth Adapter

> Execute automation through each user's wallet-native permission model instead of asking wallets to trust one global executor shape.

## Metadata

| Property | Value |
|----------|-------|
| Category | access-control |
| Tags | access-control, automation, wallet, safe, dsproxy, auth-adapter |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Automation must act through user-owned wallets or proxies
- Different wallet families expose different auth and module mechanisms
- The automation executor should not custody user funds directly
- Wallet-specific permission grants can be added and revoked around execution

## Avoid When

- The executor target, calldata, or recipe is not constrained
- Wallet permissions are broad and remain active indefinitely
- The adapter can upgrade itself without wallet consent
- A simpler direct user call provides the same UX

## How It Works

Use a small adapter per wallet family to grant just enough authority for the automation path:

```solidity
interface WalletAuthAdapter {
    function grant(address wallet, address executor) external;
    function revoke(address wallet, address executor) external;
}
```

The recipe executor still validates strategy hashes, registry entries, and trigger state. The adapter only translates those validated calls into DSProxy, Safe module, or wallet-native permission operations.

## Key Points

- Keep adapters wallet-specific and minimal.
- Constrain executor targets and action IDs before any wallet call.
- Revoke temporary permissions after flash-loan or callback flows.
- Treat adapter replacement as a critical permission change.
- Test each wallet family against unauthorized executor and stale permission cases.

## Source Evidence

- Defi Saver V3 uses separate permission adapters for DSProxy and Safe-style wallets so automation executes through wallet-native authority rather than a single custody contract.

## Related Patterns

- [Hash-Anchored Strategy Subscription](../automation/pattern-hash-anchored-strategy-subscription.md)
- [Hook/Callback Trust](../../ANTIPATTERNS.md#hookcallback-trust)
