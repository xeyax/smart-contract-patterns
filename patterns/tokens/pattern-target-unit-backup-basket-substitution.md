# Target-Unit Backup Basket Substitution

> Replace failed basket collateral by target unit so backing intent survives token-level default.

## Metadata

| Property | Value |
|----------|-------|
| Category | tokens |
| Tags | token, basket, collateral, default, backup |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A redeemable or index token represents a basket of economic target units
- Individual collateral tokens can default or become unavailable
- Backups should preserve the intended target exposure, not just token count
- Governance can configure primary and backup collateral by target unit

## Avoid When

- The basket is a pure governance-selected index with no stable target-unit promise
- Backup collateral is not economically substitutable
- There is no status oracle or default detection for collateral
- Rebalancing should be entirely manual and discretionary

## Trade-offs

**Pros:**
- Preserves the token's economic intent across collateral failure
- Makes backup substitution rules explicit and testable
- Avoids arbitrary manager choice during default handling

**Cons:**
- Requires collateral plugins or adapters to declare target units
- Misclassified target units can create hidden exposure changes
- Backup liquidity and oracle quality remain external risks

## How It Works

Governance configures a prime basket and backup collateral lists keyed by target unit:

```solidity
struct BasketItem {
    address collateral;
    bytes32 targetUnit;
    uint256 targetAmount;
}

mapping(bytes32 targetUnit => address[] backups) public backupCollateral;

function switchBasket() external {
    for each targetUnit in primeBasket {
        address chosen = _firstSound(primeCollateral[targetUnit], backupCollateral[targetUnit]);
        require(chosen != address(0), "no backup");
        newBasket.add(chosen, targetAmount[targetUnit]);
    }
    _activate(newBasket);
}
```

The substitution is based on the target unit such as USD, BTC, ETH, or a configured synthetic unit, not on a hard-coded one-token replacement.

## Implementation

```solidity
function _firstSound(address primary, address[] storage backups) internal view returns (address) {
    if (_isSound(primary)) return primary;
    for (uint256 i; i < backups.length; i++) {
        if (_isSound(backups[i])) return backups[i];
    }
    return address(0);
}
```

### Key Points

- Validate that primary and backup collateral declare the expected target unit.
- Reject duplicate collateral in the active basket.
- Track basket nonce or version when the active basket changes.
- Document whether target weights can be reweighted or must remain constant.
- Test default, backup selection, no-backup, and recovery paths.

## Source Evidence

- Reserve Protocol stores prime basket target names, configures backups by target name, and switches baskets through `BasketLib.nextBasket` and `BasketHandler._switchBasket` in `/private/tmp/defillama-source/reserve-protocol__protocol/contracts/p1/BasketHandler.sol` and `contracts/p1/mixins/BasketLib.sol`.
- Reserve tests and scenarios cover basket normalization and backup substitution in `/private/tmp/defillama-source/reserve-protocol__protocol/test`.

## Real-World Examples

- Reserve Protocol RToken - collateral substitutions are organized by target unit and collateral status.

## Related Patterns

- [Bounded Rebalance Auction](../vaults/pattern-bounded-rebalance-auction.md)
- [Historical Basket Redemption Nonces](./pattern-historical-basket-redemption-nonces.md)
- [Collateral Threshold Separation Requirements](../lending/req-collateral-threshold-separation.md)

## References

- See Source Evidence.
