# Round-Scoped Transferable Payout Receipts

> Mint transferable receipt NFTs for an async settlement round, then fund the round and burn receipts for pro-rata payout.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, async, withdrawal, deposit, receipt, nft, round |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Deposits or withdrawals settle only after an operator, validator, or epoch round finalizes
- Users need transferable claim receipts before final payout
- Many requests can share one finalized settlement amount
- The protocol can support receipt minting, funding, and burn-to-claim tests

## Avoid When

- Claims must be non-transferable or KYC-bound
- One request should always map to one fixed entitlement
- Receipt collection or linked-list mechanics are too complex to bound
- Users cannot tolerate round-finalization liveness risk

## Trade-offs

**Pros:**
- Gives users a transferable claim while async settlement is pending
- Lets one round fund many claims pro-rata
- Separates request accounting from final payout funding

**Cons:**
- More complex than a non-transferable request ledger
- Receipt burn, collection funding, and partial payout math need careful tests
- Transferability may be incompatible with compliance or beneficiary restrictions

## How It Works

Each request mints a receipt associated with a settlement round. When the round is
finalized, the protocol funds the receipt collection with the assets or shares
owed to that round. A holder burns a receipt to claim its pro-rata payout.

```solidity
function requestWithdraw(uint256 shares) external returns (uint256 receiptId) {
    uint256 round = currentRound;
    _burnShares(msg.sender, shares);
    receiptId = payoutReceipts.mint(msg.sender, round, shares);
    pendingShares[round] += shares;
}

function finalizeRound(uint256 round, uint256 assets) external onlyOperator {
    require(round < currentRound, "active round");
    payoutReceipts.fundRound(round, assets);
}

function claim(uint256 receiptId) external {
    Receipt memory r = payoutReceipts.burn(receiptId, msg.sender);
    uint256 assets = r.shares * fundedAssets[r.round] / totalShares[r.round];
    _pay(msg.sender, assets);
}
```

## Implementation

- Bind every receipt to an immutable round id and request amount.
- Finalize a round once, then fund its receipt collection before claims.
- Burn or close the receipt before transferring payout.
- Keep aggregate pending amount and receipt supply consistent.
- Bound receipt traversal, collection funding, and claim gas.
- Document whether receipt transfer changes beneficiary, receiver, or only claim ownership.

## Source Evidence

- TON liquid staking finalizes deposit and withdrawal rounds in `/private/tmp/defillama-source/ton-blockchain__liquid-staking-contract/contracts/pool.func` and mints payout receipts through `/private/tmp/defillama-source/ton-blockchain__liquid-staking-contract/contracts/pool_mint_helpers.func`.
- TON payout NFT collection and item contracts mint and burn round receipts in `/private/tmp/defillama-source/ton-blockchain__liquid-staking-contract/contracts/payout_nft/nft-collection.func` and `payout_nft/nft-item.func`.
- TON tests cover receipt behavior in `/private/tmp/defillama-source/ton-blockchain__liquid-staking-contract/tests/SmokeNFT.spec.ts` and `tests/Integrational.spec.ts`.

## Real-World Examples

- TON liquid staking - round-scoped deposit and withdrawal payout NFTs.

## Related Patterns

- [Async Deposit/Withdrawal](./pattern-async-deposit.md)
- [Operator-Finalized Withdrawal Claim](./pattern-operator-finalized-withdrawal-claim.md)
- [Withdrawal Liquidity Buffer](./pattern-withdrawal-liquidity-buffer.md)

## References

- See Source Evidence.
