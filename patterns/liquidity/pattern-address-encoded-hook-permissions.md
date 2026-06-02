# Address-Encoded Hook Permissions

> Encode a hook contract's lifecycle permissions into its address bits and validate that returned selectors match the invoked hook.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | hooks, permissions, amm, address, callback |
| Complexity | High |
| Gas Efficiency | High |
| Audit Risk | High |

## Use When

- Hook capabilities must be known before pool initialization
- Hook calls are performance-sensitive and should avoid storage lookups
- Hook deployment can grind or choose addresses with required permission bits
- Dependent capabilities can be rejected at initialization

## Avoid When

- Hook addresses are assigned unpredictably and cannot encode permissions
- Hook permissions need frequent governance changes after deployment
- Address-bit permissions would be mistaken for hook trustlessness

## How It Works

Low address bits declare which lifecycle callbacks the hook implements:

```solidity
function permissions(address hook) internal pure returns (HookPermissions memory p) {
    uint160 bits = uint160(hook);
    p.beforeSwap = bits & BEFORE_SWAP_FLAG != 0;
    p.afterSwap = bits & AFTER_SWAP_FLAG != 0;
    p.afterSwapReturnsDelta = bits & AFTER_SWAP_RETURNS_DELTA_FLAG != 0;
}

function callBeforeSwap(address hook, bytes calldata data) internal {
    if (!permissions(hook).beforeSwap) return;
    bytes4 selector = IHook(hook).beforeSwap(data);
    require(selector == IHook.beforeSwap.selector, "bad hook return");
}
```

Invalid dependent permissions, such as returning deltas without the corresponding hook, are rejected during pool setup.

### Registered Hook Flag Variant

Some pool managers store hook permissions as registered capability flags instead
of deriving them from address bits. The safety rule is the same: flags are an
initialization-time capability declaration, not proof that the hook is benign.
Registration should reject inconsistent flag combinations, require hook opt-in,
and validate success selectors or success booleans on every invoked hook path.

## Key Points

- Validate permission-bit combinations when the pool is initialized.
- Require hook return values to match expected selectors.
- Keep hook trust, upgradeability, and external-call risk explicit.
- Treat address bits as capability declaration, not authorization that the hook is safe.
- Test zero-address hooks, invalid dependent flags, and wrong selector returns.
- If permissions are stored as registration flags, require hook acceptance and
  validate every hook result just as strictly as address-bit hooks.

## Source Evidence

- Uniswap V4 encodes hook lifecycle permissions in hook address bits, rejects invalid dependent flags, and validates hook return selectors in hook tests.
- Balancer V3 stores hook capability flags in vault hook configuration, requires
  hook opt-in, and validates hook success/results through `/private/tmp/defillama-source/balancer__balancer-v3-monorepo/pkg/interfaces/contracts/vault/VaultTypes.sol:53-85`,
  `/private/tmp/defillama-source/balancer__balancer-v3-monorepo/pkg/interfaces/contracts/vault/IHooks.sol:18-57`,
  and `/private/tmp/defillama-source/balancer__balancer-v3-monorepo/pkg/vault/contracts/lib/HooksConfigLib.sol:167-198`.

## Related Patterns

- [Hook-Returned Custom Accounting Deltas](./pattern-hook-returned-custom-accounting-deltas.md)
- [Hook-Governed Dynamic LP Fee](./pattern-hook-governed-dynamic-lp-fee.md)
- [Hook/Callback Trust](../../ANTIPATTERNS.md#hookcallback-trust)
