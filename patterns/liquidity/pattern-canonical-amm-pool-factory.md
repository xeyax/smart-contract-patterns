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
  the accepted pool configuration in `/private/tmp/defillama-source/balancer__balancer-v3-monorepo/pkg/pool-utils/contracts/BasePoolFactory.sol:13-42`,
  `/private/tmp/defillama-source/balancer__balancer-v3-monorepo/pkg/pool-utils/contracts/BasePoolFactory.sol:96-167`,
  and `/private/tmp/defillama-source/balancer__balancer-v3-monorepo/pkg/vault/contracts/VaultExtension.sol:181-341`.
- Balancer V2 pool registration validates ordered tokens and duplicates through
  `/private/tmp/defillama-source/balancer__balancer-v2-monorepo/pkg/vault/contracts/PoolRegistry.sol:24-36`
  and `/private/tmp/defillama-source/balancer__balancer-v2-monorepo/pkg/vault/contracts/PoolTokens.sol:30-145`.
- Trader Joe V2 keys canonical Liquidity Book pairs by sorted tokens and bin
  step, gates pair creation through presets and quote assets, and carries
  version/bin-step metadata through routing in `/private/tmp/defillama-source/traderjoe-xyz__joe-v2/src/LBFactory.sol:52-68`,
  `/private/tmp/defillama-source/traderjoe-xyz__joe-v2/src/LBFactory.sol:184-225`,
  and `/private/tmp/defillama-source/traderjoe-xyz__joe-v2/src/LBFactory.sol:330-390`.
- Aerodrome V1 creates deterministic sorted-token pools in `/private/tmp/defillama-source/aerodrome-finance__contracts/contracts/factories/PoolFactory.sol` and constrains factory-path migration in `/private/tmp/defillama-source/aerodrome-finance__contracts/contracts/factories/FactoryRegistry.sol`.

## Related Patterns

- [Verified Callback Settlement](./pattern-verified-callback-settlement.md)
- [Deterministic Cross-Chain Factory](../cross-chain/pattern-deterministic-cross-chain-factory.md)
- [Clone Factory](../vaults/pattern-clone-factory.md)
