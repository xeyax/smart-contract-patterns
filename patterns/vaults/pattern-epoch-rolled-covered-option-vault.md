# Epoch-Rolled Covered Option Vault

> Roll vault collateral into short option positions on discrete epochs, auction the minted options, and settle round price-per-share after expiry.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, options, covered-call, epoch, auction, rollover |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Vault collateral is sold as covered calls, puts, or similar short option exposure
- Deposits and withdrawals should settle at round boundaries
- A keeper can select or commit the next option before rolling collateral
- Option sale proceeds should be auctioned rather than filled by a single manager price

## Avoid When

- Users need continuous same-block deposit and withdrawal liquidity
- Option selection, pricing, or settlement depends on unchecked owner discretion
- The option venue cannot provide deterministic expiry and settlement accounting
- A failed auction would leave the vault with unhandled option inventory

## Trade-offs

**Pros:**
- Separates user share accounting from option expiry and settlement
- Keeps option minting and auction settlement in a repeatable epoch lifecycle
- Lets queued deposits avoid taking losses from the just-expired option round

**Cons:**
- Requires keeper liveness for close, commit, roll, auction, and burn steps
- Round accounting, pending deposits, and queued withdrawals are easy to mis-order
- Strike selectors, premium pricers, and auctions are privileged economic inputs

## How It Works

At epoch close, settle the previous short option and compute the next round's price per share:

```solidity
function closeRound() external onlyKeeper {
    _settleCurrentShort();
    RoundState memory r = _rolloverAccounting();
    pricePerShare[round] = r.pricePerShare;
    lockedAmount = r.newLockedAmount;
    queuedWithdrawals = r.queuedWithdrawAmount;
}
```

After close, commit the next option from a strike selector or bounded override. Rolling to the next option deposits the locked collateral into the option venue, mints short option tokens, and creates an auction offer:

```solidity
function rollToNextOption() external onlyKeeper {
    address option = nextOption;
    currentOption = option;
    nextOption = address(0);

    _createShort(option, lockedAmount);
    auctionId = _createOffer(option);
}
```

Pending deposits mint shares using the new round price per share. Queued withdrawals are set aside before locking collateral for the next option.

## Key Points

- Keep the round state machine explicit: close old short, commit next option, roll collateral, auction, settle auction, burn leftovers.
- Compute new price per share after old short settlement and before minting queued deposit shares.
- Exclude queued withdrawal assets from performance-fee and next-round locked collateral calculations.
- Bound or timelock strike selectors, premium pricers, and manual strike overrides.
- Test in-the-money expiry, out-of-the-money expiry, failed or partial auction settlement, pending deposits, queued withdrawals, and leftover option tokens.

## Source Evidence

- Ribbon V2 closes old shorts, commits the next option, creates a new Opyn short, and auctions minted options in `/private/tmp/defillama-source/ribbon-finance__ribbon-v2/contracts/vaults/BaseVaultWithSwap/RibbonThetaVaultWithSwap.sol`.
- Ribbon V2 rollover accounting computes new locked amount, queued withdrawals, price per share, mint shares, and vault fees in `/private/tmp/defillama-source/ribbon-finance__ribbon-v2/contracts/libraries/VaultLifecycle.sol`.

## Real-World Examples

- Ribbon V2 - weekly theta vaults roll covered option exposure through Opyn short positions and option auctions.

## Related Patterns

- [Async Deposit/Withdrawal](./pattern-async-deposit.md)
- [Operator-Finalized Withdrawal Claim](./pattern-operator-finalized-withdrawal-claim.md)
- [High-Water Mark Fee](./pattern-high-water-mark-fee.md)
