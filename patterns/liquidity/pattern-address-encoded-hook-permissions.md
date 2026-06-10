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

## Trade-offs

**Pros:**
- Permission checks are pure bit masks on the hook address — no storage reads on the hot swap path.
- Capabilities are visible and immutable from the address alone, so integrators and auditors can determine hook behavior surface before pool initialization.
- Invalid dependent flag combinations are rejected once at pool setup instead of being checked on every call.
- Selector-return validation catches hooks that silently fail or return garbage on invoked paths.

**Cons:**
- Deployers must grind CREATE2 salts to land on addresses with the right permission bits, complicating deployment tooling and CI.
- Permissions are frozen at deployment; changing a hook's capability set means a new address, a new pool, and a liquidity migration.
- Address bits declare capabilities but say nothing about hook safety — an upgradeable or malicious hook passes all checks, and the flag scheme can lull integrators into misplaced trust.
- Every enabled hook point is an external call with reentrancy and gas-griefing surface that the core must defend on each swap or liquidity event.
- Bit-flag encoding consumes address space and couples the permission layout to the core's constants; adding new hook points later strains the scheme.

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
  hook opt-in, and validates hook success/results through [`pkg/interfaces/contracts/vault/VaultTypes.sol:53-85`](https://github.com/balancer/balancer-v3-monorepo/blob/0a5890a8c5d79865498d75cdc6ecdc75cf8d297d/pkg/interfaces/contracts/vault/VaultTypes.sol#L53-L85),
  [`pkg/interfaces/contracts/vault/IHooks.sol:18-57`](https://github.com/balancer/balancer-v3-monorepo/blob/0a5890a8c5d79865498d75cdc6ecdc75cf8d297d/pkg/interfaces/contracts/vault/IHooks.sol#L18-L57),
  and [`pkg/vault/contracts/lib/HooksConfigLib.sol:167-198`](https://github.com/balancer/balancer-v3-monorepo/blob/0a5890a8c5d79865498d75cdc6ecdc75cf8d297d/pkg/vault/contracts/lib/HooksConfigLib.sol#L167-L198).

## Related Patterns

- [Hook-Returned Custom Accounting Deltas](./pattern-hook-returned-custom-accounting-deltas.md)
- [Hook-Governed Dynamic LP Fee](./pattern-hook-governed-dynamic-lp-fee.md)
- [Hook/Callback Trust](../../ANTIPATTERNS.md#hookcallback-trust)
