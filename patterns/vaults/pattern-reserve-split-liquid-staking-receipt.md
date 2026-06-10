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

## Trade-offs

**Pros:**
- User claims and protocol reserve are accounted separately, so reserve operations cannot silently dilute user redemption rights.
- Per-user reserved tracking preserves exact attribution even as the aggregate reserve moves.
- Atomic reserve migration keeps tracked totals and the holder address from diverging mid-move.
- Deterministic drift sync gives a defined reconciliation path instead of ad hoc balance fixes.

**Cons:**
- Two parallel ledgers (per-user reserved map plus aggregate reserve) must agree with actual token balances; every mint, burn, and migration is a consistency obligation.
- Sync-before-mutate ordering is load-bearing: any path that burns or migrates without reconciling drift first corrupts reserve accounting.
- Extra storage writes per provide/redeem (per-user reserved plus total) raise gas on hot paths.
- Reserve-address migration and rate updates are powerful admin levers; without bounds and timelocks they become a drain vector, so governance hardening is part of the pattern's cost.
- Receipt balances visible on-chain no longer equal user-redeemable amounts, complicating integrations and explorer-level reasoning.

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
