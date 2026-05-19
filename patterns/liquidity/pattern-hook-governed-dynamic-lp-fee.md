# Hook-Governed Dynamic LP Fee

> Let a pool mark its LP fee as dynamic, then restrict stored fee updates and per-swap fee overrides to the pool's trusted hook.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, fees, hooks, dynamic-fee, governance |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Pool fees should react to volatility, inventory, order flow, or external signals
- Fee logic belongs to a hook selected at pool initialization
- The manager can distinguish stored fee updates from per-swap overrides
- Users can inspect hook identity before routing through the pool

## Avoid When

- Fee changes should be governed through delayed parameter updates only
- Hook logic is upgradeable or opaque without user-visible risk controls
- Fees can exceed documented caps or bypass router slippage checks

## How It Works

The pool is initialized with a dynamic-fee sentinel. Only the pool's hook can update the stored fee, and the hook may return a bounded fee override for a specific swap:

```solidity
function updateDynamicLPFee(PoolKey memory key, uint24 newFee) external {
    require(msg.sender == address(key.hook), "only hook");
    require(key.fee == DYNAMIC_FEE_FLAG, "not dynamic");
    require(newFee <= MAX_LP_FEE, "fee too high");
    pools[key.toId()].lpFee = newFee;
}

function beforeSwap(...) external returns (bytes4, uint24 overrideFee) {
    return (this.beforeSwap.selector, _boundedFeeForSwap());
}
```

Another variant computes the fee through the configured hook on each swap without
mutating a stored Uniswap-style dynamic-fee sentinel. The pool must still opt
into dynamic swap fees, the returned fee must be bounded by the protocol maximum,
and routers should surface that the fee is hook-determined at execution time.

## Key Points

- Mark dynamic-fee pools explicitly at initialization.
- Restrict stored fee updates to the configured hook.
- Bound per-swap fee overrides and stored fee values.
- Surface hook identity and dynamic-fee status to routers and frontends.
- Cross-check with formula-based dynamic fees, but do not merge the two mechanisms.
- Treat per-swap hook-computed fees as execution-time price inputs and keep
  user slippage bounds active.

## Source Evidence

- Uniswap V4 uses a dynamic-fee sentinel, hook-only stored LP fee updates, and bounded per-swap override fees returned from hooks.
- Balancer V3 supports hook-computed dynamic swap fees bounded by the vault's fee
  limits without relying on the Uniswap stored-fee sentinel mutation path in
  `/private/tmp/defillama-source/balancer__balancer-v3-monorepo/pkg/interfaces/contracts/vault/IHooks.sol:174-251`
  and `/private/tmp/defillama-source/balancer__balancer-v3-monorepo/pkg/vault/contracts/lib/HooksConfigLib.sol:310-366`.

## Related Patterns

- [Address-Encoded Hook Permissions](./pattern-address-encoded-hook-permissions.md)
- [Off-Peg Dynamic Fee](./pattern-offpeg-dynamic-fee.md)
- [Bounded Timelocked Parameter Change](../access-control/pattern-bounded-timelocked-parameter-change.md)
