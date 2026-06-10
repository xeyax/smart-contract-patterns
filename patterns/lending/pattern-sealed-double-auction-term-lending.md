# Sealed Double-Auction Term Lending

> Match fixed-maturity borrowers and lenders through sealed bid and offer lockers, then clear the auction at a uniform rate.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, auction, fixed-maturity, sealed-bid, repo |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A market needs fixed-term borrowing and lending at auction-discovered rates
- Borrower bids and lender offers should be hidden before auction close
- Collateral and purchase-token compatibility can be checked before settlement
- The auction can run in phases with distinct locker and clearing roles

## Avoid When

- Maturity, collateral, or purchase-token terms are negotiated bilaterally
- Bids or offers need continuous public order-book updates
- Participants cannot tolerate failed fills or partial clearing
- The protocol cannot prevent late submissions or post-close mutation

## Trade-offs

**Pros:**
- Reduces mempool-visible rate extraction before clearing
- Produces one clearing result across many borrowers and lenders
- Separates order custody from clearing and repo servicing

**Cons:**
- More operational phases than continuous lending
- Requires careful locked-order cancellation and reveal rules
- Clearing failure can strand a whole auction cohort until recovery

## How It Works

Borrowers lock bids and lenders lock offers into separate contracts before the
auction deadline. The auction clears only after both sides are fixed:

```solidity
function lockBid(bytes32 bidId, Bid calldata bid) external {
    require(block.timestamp < auctionClose, "closed");
    _validateCollateral(bid);
    bids[bidId] = hashBid(bid);
    _escrowCollateral(bid.borrower, bid.collateral);
}

function lockOffer(bytes32 offerId, Offer calldata offer) external {
    require(block.timestamp < auctionClose, "closed");
    offers[offerId] = hashOffer(offer);
    _escrowPurchaseToken(offer.lender, offer.amount);
}

function clearAuction(Clearing calldata clearing) external onlyAuctioneer {
    require(block.timestamp >= auctionClose, "open");
    _verifyLockedOrders(clearing);
    _settleUniformClearingRate(clearing);
}
```

## Implementation

### Key Points

- Use separate bid and offer lockers with explicit auction phase checks.
- Bind every locked order to auction id, maturity, collateral, purchase token, amount, price/rate, and participant.
- Restrict clearing and cancellation roles separately.
- Validate collateral eligibility before accepting borrower orders.
- Test late locks, duplicate order ids, partial fills, clearing-price bounds, cancellation windows, and role separation.

## Source Evidence

- Term Finance locks borrower bids and lender offers in [`contracts/TermAuctionBidLocker.sol`](https://github.com/term-finance/term-finance-contracts/blob/262098c71578bbb9e54d6c2a8d2d88d112b9662a/contracts/TermAuctionBidLocker.sol) and [`contracts/TermAuctionOfferLocker.sol`](https://github.com/term-finance/term-finance-contracts/blob/262098c71578bbb9e54d6c2a8d2d88d112b9662a/contracts/TermAuctionOfferLocker.sol).
- Term Finance clearing logic and auction phases live in [`contracts/TermAuction.sol`](https://github.com/term-finance/term-finance-contracts/blob/262098c71578bbb9e54d6c2a8d2d88d112b9662a/contracts/TermAuction.sol).
- Term Finance Certora specs cover auction roles and bid locking under [`certora/specs/termAuction`](https://github.com/term-finance/term-finance-contracts/blob/262098c71578bbb9e54d6c2a8d2d88d112b9662a/certora/specs/termAuction) and `termAuctionBidLocker`.

## Real-World Examples

- Term Finance - fixed-maturity repo lending auctions with bid and offer lockers.

## Related Patterns

- [Rolling Fixed-Maturity Debt Tokens](./pattern-rolling-fixed-maturity-debt-tokens.md)
- [Mempool-Visible Value Transfer](../../ANTIPATTERNS.md#mempool-visible-value-transfer)

## References

- See Source Evidence.
