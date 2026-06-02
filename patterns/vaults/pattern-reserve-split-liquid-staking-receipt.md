# Reserve Split Liquid Staking Receipt

> Track user-owned and protocol-reserved receipt-token supply separately when a liquid-staking or CDP wrapper keeps part of minted receipts in reserve.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, liquid-staking, reserve, receipt-token, cdp |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- A wrapper mints receipt tokens while retaining part of the receipt supply as protocol reserve
- User balances and reserved balances need different redemption or collateral semantics
- The reserve address can migrate
- Exchange-rate drift can create receipt balance differences that need reconciliation

## Avoid When

- All minted receipts belong directly to users
- The reserve holder has unrestricted withdrawal rights
- Managers can change receipt rates or reserve addresses without bounds
- The wrapper cannot reconcile receipt balance drift deterministically

## How It Works

Track per-user reserved receipts and aggregate reserve supply:

```solidity
function provide(address user, uint256 assets) external {
    (uint256 userReceipts, uint256 reserveReceipts) = _quoteReceipts(assets);
    reservedReceipt[user] += reserveReceipts;
    totalReservedReceipts += reserveReceipts;
    _mint(user, userReceipts);
    _mint(reserveAddress, reserveReceipts);
}

function migrateReserve(address newReserve) external onlyGovernance {
    uint256 amount = receipt.balanceOf(reserveAddress);
    _moveReserve(reserveAddress, newReserve, amount);
    reserveAddress = newReserve;
}
```

Sync logic reconciles actual reserve balance against tracked reserves before minting, burning, or migrating.

## Key Points

- Track per-user reserved receipts as well as total reserve.
- Bound and timelock exchange-rate, user-rate, and reserve-address updates.
- Reconcile reserve drift before burning or migrating reserve balances.
- Make reserve migration atomic so tracked reserves and holder address cannot diverge.
- Test partial burns, sync drift, reserve migration, and manager misconfiguration.

## Source Evidence

- Lista's slisBNB provider tracks user reserved receipt balances and total reserve, syncs receipt drift, and migrates the reserve address atomically.

## Related Patterns

- [Operator-Routed Liquid Staking Share](./pattern-operator-routed-liquid-staking-share.md)
- [Liquid Staking Loss Accounting Requirements](./req-liquid-staking-loss-accounting.md)
- [Unrestricted Admin](../../ANTIPATTERNS.md#unrestricted-admin)
