# Packed Reserve Risk Configuration

> Pack reserve risk parameters and operational flags into a named config word with masks, bounds, decode helpers, and setter validation.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, reserve, configuration, bitmask, risk |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- A reserve has many hot-path risk parameters or operational flags
- Gas cost matters for reads inside borrow, liquidation, and account-health checks
- Every packed field can have a stable bit range and named helper
- Admin setters can validate each decoded value independently

## Avoid When

- Field semantics are still changing frequently
- Bit ranges are undocumented or reused for unrelated meanings
- Setters write raw words without field-level bounds
- Off-chain tooling cannot decode configuration changes

## Trade-offs

**Pros:**
- Reduces storage reads in hot risk paths
- Makes reserve configuration snapshots compact
- Encourages named getters and setters for each field

**Cons:**
- Bit shifts and masks are easy to get wrong
- Storage-layout upgrades are more constrained
- Raw config changes can hide critical parameter updates from reviewers

## How It Works

Store multiple reserve parameters in one word, but expose only typed helpers that
mask, shift, bound, and decode each field.

```solidity
uint256 constant LTV_MASK = 0xffff;
uint256 constant LIQ_THRESHOLD_MASK = 0xffff << 16;
uint256 constant ACTIVE_BIT = 1 << 56;

function setLtv(DataTypes.ReserveConfigurationMap memory self, uint256 ltv) internal pure {
    require(ltv <= MAX_VALID_LTV, "ltv");
    self.data = (self.data & ~LTV_MASK) | ltv;
}

function getFlags(DataTypes.ReserveConfigurationMap memory self)
    internal
    pure
    returns (bool active, bool frozen, bool borrowingEnabled)
{
    active = self.data & ACTIVE_BIT != 0;
    // decode other flags from named bit positions
}
```

Admin configuration functions should validate relationships across fields after
decoding, not only individual bit ranges.

## Implementation

- Document every bit range in source and deployment docs.
- Use named masks, shifts, and max values instead of raw literals at call sites.
- Keep raw-word setters unavailable or heavily restricted.
- Validate cross-field relationships such as LTV, liquidation threshold, and bonus.
- Emit events with decoded old and new values for monitoring.
- Test each field boundary, mask isolation, and invalid cross-field combinations.

## Source Evidence

- Aave V2 packs reserve LTV, liquidation threshold, bonus, decimals, active/frozen/borrowing/stable-rate flags, and reserve factor into a configuration word in `/private/tmp/defillama-source/aave__protocol-v2/contracts/protocol/libraries/types/DataTypes.sol`.
- Aave V2 defines masks, bounds, decode helpers, and configurator validation in `contracts/protocol/libraries/configuration/ReserveConfiguration.sol` and `contracts/protocol/lendingpool/LendingPoolConfigurator.sol`.

## Real-World Examples

- Aave V2 uses packed reserve configuration for lending risk parameters and operational flags.

## Related Patterns

- [Comptroller Risk Gate](./pattern-comptroller-risk-gate.md)
- [Collateral Threshold Separation Requirements](./req-collateral-threshold-separation.md)
- [Stale-State Bound Check](../../ANTIPATTERNS.md#stale-state-bound-check)

## References

- Aave V2 reserve configuration source.
