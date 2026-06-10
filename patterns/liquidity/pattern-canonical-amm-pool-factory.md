# Canonical AMM Pool Factory

> Create each AMM pool at a deterministic canonical address or id keyed by sorted token pair and immutable pool parameters.

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
- Each token pair and immutable parameter set should have at most one canonical pool
- Routers and callbacks need to derive and verify pool addresses
- Tick spacing or other immutable parameters are tied to fee tiers

## Avoid When

- Pools are intentionally non-canonical or strategy-specific
- Governance cannot curate fee tiers or tick spacing
- Pool address derivation depends on mutable configuration

## Trade-offs

**Pros:**
- Routers and callbacks verify pool identity by recomputing the CREATE2 address — no registry storage read and no trust in `msg.sender` claims.
- One canonical pool per pair/parameter set concentrates liquidity instead of fragmenting it across duplicate pools.
- Deterministic addresses simplify off-chain indexing, cross-chain address prediction, and integration code.
- Immutable init parameters remove a whole class of post-deployment reconfiguration attacks.

**Cons:**
- Address derivation is welded to the exact pool bytecode (init code hash); any pool implementation change breaks every derived-address consumer and effectively requires a new factory.
- Immutability cuts both ways: a bug in pool logic cannot be patched in place, only mitigated by migrating liquidity to a new canonical deployment.
- Configurable vault/bin systems need a carefully widened canonical key (hooks, rate providers, bin step, version); choosing it too narrow blocks legitimate pools, too wide reintroduces duplicates.
- Fee tiers and tick spacings require ongoing governance curation, and each added tier multiplies the pool set routers must consider.
- Multiple approved factory paths over time fragment canonicality, so migration and reapproval constraints become part of the security model.

## How It Works

The factory sorts tokens and derives a pool address or pool id from immutable parameters:

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

A configurable vault or bin-AMM variant may need a wider canonical key than
`token0, token1, fee`. The pool identity can include a vault, hook contract,
rate providers, token configuration, pause/fee roles, bin step, or protocol
version. In those systems, "one canonical pool per pair" is too broad; the
factory should define exactly which immutable configuration makes a pool unique.

## Key Points

- Sort token addresses before deriving the key.
- Reject duplicate pools for the same token pair and parameter set.
- Bound or govern fee-tier tick spacing.
- Keep pool init parameters immutable after deployment.
- Use canonical address derivation in routers, callbacks, and off-chain indexing.
- For vault-managed pools, validate token ordering, duplicate tokens, token type
  compatibility, rate-provider compatibility, hook acceptance, and initialization
  in one registration flow.
- For bin or versioned AMMs, include bin step, version, or tier metadata in the
  pool key and route path.
- If governance can approve multiple factory paths over time, preserve canonical pool identity inside each approved path and test migration or reapproval constraints.

## Source Evidence

- Uniswap V2 derives canonical pair addresses from sorted token pairs and rejects duplicates.
- Uniswap V3 and PancakeSwap V3 factories derive canonical pools from sorted tokens and fee tiers, prevent duplicates, and use the same derivation in callback validation.
- Balancer V3 factory and vault registration show why configurable vault pools
  cannot be reduced to one canonical pool per token pair: hook config, rate
  providers, token types, pause windows, roles, and initialization are part of
  the accepted pool configuration in [`pkg/pool-utils/contracts/BasePoolFactory.sol:13-42`](https://github.com/balancer/balancer-v3-monorepo/blob/0a5890a8c5d79865498d75cdc6ecdc75cf8d297d/pkg/pool-utils/contracts/BasePoolFactory.sol#L13-L42),
  [`pkg/pool-utils/contracts/BasePoolFactory.sol:96-167`](https://github.com/balancer/balancer-v3-monorepo/blob/0a5890a8c5d79865498d75cdc6ecdc75cf8d297d/pkg/pool-utils/contracts/BasePoolFactory.sol#L96-L167),
  and [`pkg/vault/contracts/VaultExtension.sol:181-341`](https://github.com/balancer/balancer-v3-monorepo/blob/0a5890a8c5d79865498d75cdc6ecdc75cf8d297d/pkg/vault/contracts/VaultExtension.sol#L181-L341).
- Balancer V2 pool registration validates ordered tokens and duplicates through
  [`pkg/vault/contracts/PoolRegistry.sol:24-36`](https://github.com/balancer/balancer-v2-monorepo/blob/316ded078ddc2f1b28da5804d25752af67453435/pkg/vault/contracts/PoolRegistry.sol#L24-L36)
  and [`pkg/vault/contracts/PoolTokens.sol:30-145`](https://github.com/balancer/balancer-v2-monorepo/blob/316ded078ddc2f1b28da5804d25752af67453435/pkg/vault/contracts/PoolTokens.sol#L30-L145).
- Trader Joe V2 keys canonical Liquidity Book pairs by sorted tokens and bin
  step, gates pair creation through presets and quote assets, and carries
  version/bin-step metadata through routing in [`src/LBFactory.sol:52-68`](https://github.com/traderjoe-xyz/joe-v2/blob/067c6ccf5b8ff1526d03fa3e4c65ec45d01c1f73/src/LBFactory.sol#L52-L68),
  [`src/LBFactory.sol:184-225`](https://github.com/traderjoe-xyz/joe-v2/blob/067c6ccf5b8ff1526d03fa3e4c65ec45d01c1f73/src/LBFactory.sol#L184-L225),
  and [`src/LBFactory.sol:330-390`](https://github.com/traderjoe-xyz/joe-v2/blob/067c6ccf5b8ff1526d03fa3e4c65ec45d01c1f73/src/LBFactory.sol#L330-L390).
- Aerodrome V1 creates deterministic sorted-token pools in [`contracts/factories/PoolFactory.sol`](https://github.com/aerodrome-finance/contracts/blob/1ba30815bba620f7e9faa34769ffd00c214c9b82/contracts/factories/PoolFactory.sol) and constrains factory-path migration in [`contracts/factories/FactoryRegistry.sol`](https://github.com/aerodrome-finance/contracts/blob/1ba30815bba620f7e9faa34769ffd00c214c9b82/contracts/factories/FactoryRegistry.sol).

## Related Patterns

- [Verified Callback Settlement](./pattern-verified-callback-settlement.md)
- [Deterministic Cross-Chain Factory](../cross-chain/pattern-deterministic-cross-chain-factory.md)
- [Clone Factory](../vaults/pattern-clone-factory.md)
