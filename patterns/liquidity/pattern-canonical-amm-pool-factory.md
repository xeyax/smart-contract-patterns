# Canonical AMM Pool Factory

> Create each AMM pool at a deterministic canonical address keyed by sorted token pair, fee tier, and tick spacing.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, factory, create2, pool, callback |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- A protocol supports many pools with identical logic
- Each token pair and fee tier should have at most one canonical pool
- Routers and callbacks need to derive and verify pool addresses
- Tick spacing or other immutable parameters are tied to fee tiers

## Avoid When

- Pools are intentionally non-canonical or strategy-specific
- Governance cannot curate fee tiers or tick spacing
- Pool address derivation depends on mutable configuration

## How It Works

The factory sorts tokens and derives a pool address from immutable parameters:

```solidity
require(tokenA != tokenB, "same token");
(address token0, address token1) = sort(tokenA, tokenB);
bytes32 salt = keccak256(abi.encode(token0, token1, fee));
pool = create2(poolBytecode, salt);
```

Periphery contracts use the same formula to validate callbacks:

```solidity
require(msg.sender == computePool(factory, token0, token1, fee), "bad pool");
```

## Key Points

- Sort token addresses before deriving the key.
- Reject duplicate pools for the same token pair and fee tier.
- Bound or govern fee-tier tick spacing.
- Keep pool init parameters immutable after deployment.
- Use canonical address derivation in routers, callbacks, and off-chain indexing.

## Source Evidence

- Uniswap V3 and PancakeSwap V3 factories derive canonical pools from sorted tokens and fee tiers, prevent duplicates, and use the same derivation in callback validation.

## Related Patterns

- [Verified Callback Settlement](./pattern-verified-callback-settlement.md)
- [Deterministic Cross-Chain Factory](../cross-chain/pattern-deterministic-cross-chain-factory.md)
- [Clone Factory](../vaults/pattern-clone-factory.md)
