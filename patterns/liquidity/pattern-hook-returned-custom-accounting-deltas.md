# Hook-Returned Custom Accounting Deltas

> Let trusted AMM hooks return signed token deltas that the singleton manager settles through the same net-delta ledger as core swaps.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | hooks, accounting, deltas, amm, settlement |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Hooks need to implement fees, wrappers, curves, or other custom accounting
- The core manager can enforce end-of-operation settlement for hook deltas
- Hook capabilities are declared and validated before pool use
- Users and integrators can choose whether to trust a hook-enabled pool

## Avoid When

- Hook code is untrusted but can debit users or pool balances
- The manager cannot distinguish user, pool, and hook deltas
- Returned deltas bypass slippage or authorization checks

## Trade-offs

**Pros:**
- Hooks can implement fees, wrappers, and custom curves without forking the core manager or duplicating settlement logic.
- All hook obligations flow through the same net-delta ledger, so one end-of-frame solvency check covers core and hook accounting alike.
- Declared hook permissions and selector validation make the capability surface explicit and verifiable at pool creation.
- Opt-in adjusted-amount variants let conservative vaults expose a narrower, easier-to-bound interface than arbitrary deltas.

**Cons:**
- Returned deltas are value-moving instructions: a malicious or buggy hook can debit users up to whatever the slippage bounds permit.
- Slippage checks must run after adjustment and handle signed deltas in both directions; naive min-out/max-in checks silently miss negative-delta cases.
- Per-pool hook trust fragments composability — integrators must vet each hook-enabled pool individually instead of trusting the protocol once.
- Test surface grows substantially: wrong-sign returns, unsettled deltas, inconsistent selector responses, and adjusted-amount/liquidity-mode interactions all need coverage.
- Extra external calls and delta bookkeeping per lifecycle event add gas over hookless pools.

## How It Works

After a lifecycle event, the manager applies signed deltas returned by the hook:

```solidity
function _afterSwap(PoolKey memory key, SwapParams memory params) internal {
    (bytes4 selector, int256 userDelta, int256 hookDelta) = key.hook.afterSwap(params);
    require(selector == IHook.afterSwap.selector, "bad selector");

    _accountDelta(msg.sender, key.currency0, userDelta);
    _accountDelta(address(key.hook), key.currency0, hookDelta);
}
```

The operation remains inside the manager's settlement frame, so all hook-created obligations must settle before exit.

Vault hook systems can expose a narrower variant where hooks return adjusted
amounts rather than arbitrary accounting deltas. Those adjusted amounts still
move value: the manager must opt the pool into adjusted amounts, verify hook
success and return length, apply user min/max checks after the adjustment, and
disable liquidity modes whose safety checks do not compose with adjusted
amounts.

## Key Points

- Treat returned deltas as value-moving instructions from trusted hook logic.
- Enforce selector returns and declared hook permissions.
- Apply user slippage checks after custom accounting changes the effective amount, and check the signed direction of hook deltas explicitly.
- Keep hook deltas inside the same settlement invariant as core pool deltas.
- Test malicious or inconsistent hook returns, wrong sign, and unsettled deltas.
- Do not assume naive min-out or max-in checks cover positive and negative hook deltas symmetrically.
- For hook-adjusted amounts, run user slippage or limit checks after the hook
  adjustment and reject modes that cannot be bounded after adjustment.

## Source Evidence

- Uniswap V4 allows hooks to return custom accounting deltas during liquidity and swap operations while the pool manager remains the common settlement layer.
- PancakeSwap Infinity Periphery validates min-out and max-in with signed delta handling in [`src/libraries/SlippageCheck.sol`](https://github.com/pancakeswap/infinity-periphery/blob/f39aef4a1be63e5404e686bf621436bbfe58f6aa/src/libraries/SlippageCheck.sol).
- Balancer V3 hook-adjusted amount paths are explicitly opt-in, validate hook
  success and return data, apply user limits after adjustment, and disable
  unbalanced liquidity where adjusted amounts would bypass safety assumptions in
  [`pkg/interfaces/contracts/vault/IHooks.sol:118-144`](https://github.com/balancer/balancer-v3-monorepo/blob/0a5890a8c5d79865498d75cdc6ecdc75cf8d297d/pkg/interfaces/contracts/vault/IHooks.sol#L118-L144),
  [`pkg/interfaces/contracts/vault/IHooks.sol:174-251`](https://github.com/balancer/balancer-v3-monorepo/blob/0a5890a8c5d79865498d75cdc6ecdc75cf8d297d/pkg/interfaces/contracts/vault/IHooks.sol#L174-L251),
  and [`pkg/vault/contracts/lib/HooksConfigLib.sol:213-278`](https://github.com/balancer/balancer-v3-monorepo/blob/0a5890a8c5d79865498d75cdc6ecdc75cf8d297d/pkg/vault/contracts/lib/HooksConfigLib.sol#L213-L278).

## Related Patterns

- [Address-Encoded Hook Permissions](./pattern-address-encoded-hook-permissions.md)
- [Net Delta Settlement Invariants](./req-net-delta-settlement-invariants.md)
- [Missing Slippage Protection](../../ANTIPATTERNS.md#missing-slippage-protection)
