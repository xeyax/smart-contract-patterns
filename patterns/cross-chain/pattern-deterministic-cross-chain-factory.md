# Deterministic Cross-Chain Factory

> Deploy peer contract systems at predictable addresses across chains so cross-chain configuration can be precomputed and verified.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, factory, create2, create3, deterministic-address, peers |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- The same protocol graph is deployed on multiple chains
- Peers need to know each other's addresses before messages can be sent
- Deployment parameters and role labels should be part of the address domain
- Integrators need stable addresses across repeatable deployments

## Avoid When

- Chain-specific VM behavior breaks deterministic bytecode assumptions
- Constructor args or bytecode contain dynamic values that cannot be reproduced
- A canonical bridge already registers peers through a safer registry

## Trade-offs

**Pros:**
- Enables preconfigured cross-chain peers
- Makes deployment reproducible and audit-friendly
- Reduces manual address wiring mistakes

**Cons:**
- Salt design becomes security-critical
- Same-parameter collisions must be handled explicitly
- Some chains have CREATE2/CREATE3 compatibility quirks
- Deployment bugs can be repeated across chains

## How It Works

The factory computes salts from a complete deployment domain:

```solidity
bytes32 salt = keccak256(abi.encode(
    version,
    deployer,
    roleLabel,
    tokenName,
    tokenSymbol,
    managerAddress,
    externalSalt
));
```

It then deploys the cross-chain components through deterministic primitives:

```solidity
manager = CREATE3.deploy(managerSalt, managerBytecode);
transceiver = CREATE3.deploy(transceiverSalt, transceiverBytecode);
```

When an immutable messenger is deployed at the same address on every chain, that
address can become part of endpoint authentication. This should be reserved for
protocols that can reproduce bytecode and address derivation exactly across
chains; otherwise use explicit counterpart registration instead.

## Key Points

- Include version and deployer in salts unless true global address reuse is intended.
- Include role labels so different components cannot collide.
- Test same-parameter collision and different-salt success.
- Expose address prediction functions for off-chain peer configuration.
- Validate exact message fees during peer setup; excess or short payment should fail closed.
- Keep staged bytecode immutable or versioned if stored on-chain for deployment.
- For retryable-ticket deployment, reserve enough destination gas, isolate nonce/address derivation through a dedicated sender, and make resends idempotent so expired or out-of-order retryables do not rewrite finalized mappings.
- Constructor-agnostic proxies can keep deterministic wrapped-token addresses stable while initialization binds token metadata and bridge authority after deployment.
- Same-address immutable messengers can authenticate the remote endpoint by comparing the bridge-reported origin sender to `address(this)`, but only when deployment artifacts prove identical bytecode and address reuse.

## Source Evidence

- Wormhole NTT uses deterministic deployment for factory and NTT components across chains.
- Its salts bind version, deployer, role labels, token metadata, manager address, and external salt, with tests for collisions and successful different-salt deployments.
- Arbitrum's atomic token bridge deployment flow uses retryable-ticket deployment, dedicated retryable sender contracts, idempotent resend logic, and tests for failed deployment, frontrun, and already-existing deterministic contracts.
- Polygon zkEVM/Agglayer deploys wrapped-token proxies deterministically with constructor-agnostic bytecode and initializes bridge-owned token metadata through the bridge in `/private/tmp/defillama-source/0xPolygonHermez__zkevm-contracts/contracts/lib/TokenWrappedTransparentProxy.sol` and `contracts/AgglayerBridge.sol`.
- Avalanche ICM Teleporter documents universal same-address deployment for `TeleporterMessenger` and uses that invariant in endpoint authentication in `/private/tmp/defillama-source/ava-labs__icm-contracts/contracts/teleporter/README.md` and `contracts/teleporter/TeleporterMessenger.sol`.

## Related Patterns

- [Chain-Bound Request Hash](./pattern-chain-bound-request-hash.md)
- [Bootstrap Authority Handoff](../access-control/pattern-bootstrap-authority-handoff.md)
- [Clone Factory](../vaults/pattern-clone-factory.md)
