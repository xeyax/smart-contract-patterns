# Clone Factory (EIP-1167 Vault Deployment)

> Mass deployment of parameterized vault instances via minimal proxy clones — ~45K gas per vault instead of ~2M.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | EIP-1167, factory, clones, deployment, referral |
| Complexity | Low |
| Gas Efficiency | High |
| Audit Risk | Low |

## Use When

- Many vaults with identical logic but different parameters (fee tiers, recipients, names)
- Referral/whitelabel programs — each partner gets their own vault cheaply
- On-chain registry of all deployed vaults is needed (factory emits events)
- Deploy gas cost matters (e.g. deploying 50+ vaults)

## Avoid When

- Each vault needs independent upgradeability (use UUPS or Beacon proxy instead)
- Vaults have different logic, not just different parameters
- Only 1-2 vaults needed (direct deployment is simpler)

## Trade-offs

**Pros:**
- Deploy cost: ~45K gas per clone vs ~2M for full contract
- All clones share one audited implementation — single audit covers all instances
- Factory serves as on-chain registry via events
- Simple: no proxy admin, no upgrade slots, no storage collision risk

**Cons:**
- Clones are NOT upgradeable — to fix a bug, deploy new implementation and migrate users
- Slight gas overhead per call (~700 gas for DELEGATECALL forwarding)
- Factory is a privileged contract — compromise gives ability to deploy rogue vaults

## How It Works

### EIP-1167 Minimal Proxy

Each clone is a tiny contract (~45 bytes) that delegates all calls to the implementation:

```
DELEGATECALL to implementation ──► execute logic ──► return result
         ▲                                               │
         │              clone storage                     │
         └────────────── (own state) ◄────────────────────┘
```

Clone has its own storage but borrows all code from implementation. State is isolated — each clone is an independent vault with its own balances, HWM, fee config.

### Factory Workflow

```
                    ┌──────────────────┐
                    │  Implementation  │
                    │  (FeeWrapperVault)│
                    └────────┬─────────┘
                             │ Clones.clone()
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
   │ Clone A     │   │ Clone B     │   │ Clone C     │
   │ fee: 1000   │   │ fee: 1500   │   │ fee: 500    │
   │ recv: Alice │   │ recv: Bob   │   │ recv: Carol │
   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ▼
                      ┌─────────────┐
                      │ Base Vault  │
                      │ (strategy)  │
                      └─────────────┘
```

1. Owner calls `factory.createVault(referrer, feeBps, name, symbol)`
2. Factory clones implementation via `Clones.clone()`
3. Factory calls `clone.initialize(...)` with parameters
4. Factory whitelists clone in base vault (if base vault has access control)
5. Factory emits `VaultCreated` event — serves as on-chain registry

## Implementation

```solidity
contract FeeVaultFactory {
    using Clones for address;

    address public immutable implementation;
    IERC4626 public immutable baseVault;
    address public immutable asset;
    address public owner;

    address[] public deployedVaults;

    event VaultCreated(
        address indexed vault,
        address indexed feeRecipient,
        uint256 feeBps,
        string name
    );

    constructor(address _implementation, address _baseVault, address _owner) {
        implementation = _implementation;
        baseVault = IERC4626(_baseVault);
        asset = baseVault.asset();
        owner = _owner;
    }

    function createVault(
        address feeRecipient,
        uint256 feeBps,
        string calldata name,
        string calldata symbol
    ) external onlyOwner returns (address vault) {
        vault = implementation.clone();

        FeeWrapperVault(vault).initialize(
            address(baseVault),
            asset,
            feeRecipient,
            feeBps,
            name,
            symbol
        );

        // Auto-whitelist in base vault (factory needs MANAGER role)
        IBaseVault(address(baseVault)).addToWhitelist(vault);

        deployedVaults.push(vault);
        emit VaultCreated(vault, feeRecipient, feeBps, name);
    }

    function getDeployedVaults() external view returns (address[] memory) {
        return deployedVaults;
    }
}
```

### Key Points

- **Clone is not upgradeable — this is a feature.** Simplicity reduces audit surface. If implementation has a bug, deploy a new implementation contract and create new clones. Old clones continue working on old logic — users migrate at their own pace.
- **Factory needs MANAGER role in base vault.** Auto-whitelisting requires permission. Grant factory the minimum role needed (e.g. `WHITELIST_MANAGER`), not admin.
- **Events as registry.** `VaultCreated` events provide a complete on-chain history of all vaults. Subgraph or indexer can build a dashboard from events alone — no need to query `deployedVaults[]` array on-chain.
- **`initialize()` is one-shot.** OpenZeppelin's `initializer` modifier prevents re-initialization. Even if someone calls `initialize()` on a clone, it reverts after first call.
- **Implementation contract must not be usable directly.** Call `_disableInitializers()` in implementation's constructor to prevent direct initialization of the template.

## Variations

### Deterministic Deployment (CREATE2)

Predictable clone addresses via `cloneDeterministic()`:

```solidity
bytes32 salt = keccak256(abi.encodePacked(feeRecipient, feeBps));
vault = implementation.cloneDeterministic(salt);
```

Useful when vault address must be known before deployment (e.g. for off-chain integrations or cross-chain messaging).

### Beacon Proxy (Upgradeable Clones)

If all clones must be upgradeable simultaneously, use `BeaconProxy` instead of EIP-1167:

```
Beacon (stores implementation address)
    │
    ├── BeaconProxy A ──► implementation V1
    ├── BeaconProxy B ──► implementation V1
    └── BeaconProxy C ──► implementation V1

After upgrade:
    ├── BeaconProxy A ──► implementation V2  (automatic)
    ├── BeaconProxy B ──► implementation V2  (automatic)
    └── BeaconProxy C ──► implementation V2  (automatic)
```

Trade-off: ~100K gas per deploy (vs ~45K for EIP-1167), but all clones upgrade atomically when beacon implementation changes. Extra trust assumption — beacon owner can change all vaults at once.

## Real-World Examples

- [Morpho MetaMorpho VaultFactory](https://github.com/morpho-org/metamorpho/blob/main/src/MetaMorphoFactory.sol) — CREATE2 factory for MetaMorpho vaults
- [OpenZeppelin Clones](https://docs.openzeppelin.com/contracts/5.x/api/proxy#Clones) — reference implementation of EIP-1167
- [Yearn V3 VaultFactory](https://github.com/yearn/yearn-vaults-v3/blob/master/contracts/VaultFactory.vy) — factory deploying strategy vaults with shared blueprint

## Related Patterns

- [Vault Wrapper](./pattern-vault-wrapper.md) — the vault being cloned by this factory
- [Vault Composability Risk](./risk-vault-composability.md) — risks of many wrappers sharing one base vault

## References

- [EIP-1167: Minimal Proxy Contract](https://eips.ethereum.org/EIPS/eip-1167) — the cloning standard
- [OpenZeppelin Clones Library](https://docs.openzeppelin.com/contracts/5.x/api/proxy#Clones) — production implementation
- [EIP-1967: Proxy Storage Slots](https://eips.ethereum.org/EIPS/eip-1967) — relevant for Beacon proxy variation
