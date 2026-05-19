# Receipt-Wrapped NFT Collateral Loan

> Custody each pledged NFT in the lending protocol while minting a borrower-held receipt NFT that tracks the loan state.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, nft, collateral, receipt, auction, liquidation |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Each collateral item is unique and cannot be merged into a fungible collateral balance
- Borrowers need a receipt while the protocol custodies the pledged NFT
- Liquidation should auction the individual NFT rather than seize a pro-rata token balance
- Loan state must bind one NFT collection and token id to one debt position

## Avoid When

- Collateral is fungible or can be represented safely by ordinary collateral shares
- The receipt token would be mistaken for ownership of an unencumbered NFT
- Liquidation cannot get reliable NFT prices, bid floors, and auction timing
- The protocol cannot safely handle ERC721 receiver, wrapper, and callback behavior

## Trade-offs

**Pros:**
- Keeps per-token collateral state explicit
- Gives borrowers a transferable or displayable receipt if the design permits it
- Supports auction, redeem, repay, and default transitions per NFT

**Cons:**
- More state transitions than fungible collateral lending
- Requires collection-specific price and auction configuration
- Receipt hooks, flash-loan locks, and repay callbacks add integration risk

## How It Works

When a borrower pledges an NFT, the lending protocol transfers the underlying NFT into custody and mints a receipt NFT to the borrower:

```solidity
function createLoan(address nft, uint256 tokenId, address borrower, uint256 debt) internal {
    require(loanIdByNft[nft][tokenId] == 0, "already pledged");

    uint256 loanId = nextLoanId++;
    loanIdByNft[nft][tokenId] = loanId;

    IERC721(nft).safeTransferFrom(msg.sender, address(this), tokenId);
    receiptNft.mint(borrower, tokenId);

    loans[loanId] = Loan({
        borrower: borrower,
        nft: nft,
        tokenId: tokenId,
        debt: debt,
        state: LoanState.Active
    });
}
```

If the loan becomes unhealthy, it enters an auction state. The borrower can redeem by repaying enough debt before the auction expires, which resets the loan to active. If liquidation completes, the loan moves to defaulted, the receipt is burned, and the underlying NFT is transferred according to the auction outcome.

## Key Points

- Maintain a unique `nft -> tokenId -> loanId` mapping and clear it on repay or default.
- Update loan state before releasing the underlying NFT or calling external hooks.
- Burn the receipt when the underlying NFT leaves protocol custody.
- Lock or constrain flash loans and transfers while the NFT is in auction.
- Price and auction rules should include stale oracle handling, minimum bid deltas, reserve debt coverage, and auction extension behavior.
- Treat repayment interceptors, receiver callbacks, and wrapper contracts as privileged hook surfaces.

## Source Evidence

- BendDAO creates one loan per pledged NFT, mints a `bNFT` receipt, stores active loan state, and tracks collection/token collateral mappings in `/private/tmp/defillama-source/BendDAO__bend-lending-protocol/contracts/protocol/LendPoolLoan.sol`.
- BendDAO auction, redeem, and liquidation logic validates NFT loan health, bid amounts, auction windows, and state transitions in `/private/tmp/defillama-source/BendDAO__bend-lending-protocol/contracts/libraries/logic/LiquidateLogic.sol`.

## Real-World Examples

- BendDAO - NFT-backed lending with borrower receipt NFTs and per-token auction/liquidation state.

## Related Patterns

- [Scaled Balance Token Accounting](./pattern-scaled-balance-token-accounting.md)
- [Collateral Threshold Separation Requirements](./req-collateral-threshold-separation.md)
- [Action-Scoped Bounded Risk Prices](../oracles/pattern-action-scoped-bounded-lending-prices.md)
