# Share-Denominated Lending Accounting

> Track supply and borrow positions as market shares against total assets so interest and losses are allocated proportionally.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, shares, accounting, interest, rounding |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- A lending market needs proportional supply or borrow accounting
- Interest accrual changes total assets without iterating through positions
- Bad debt or losses should be reflected through the market exchange rate
- Virtual offsets are needed to bound first-depositor rounding

## Avoid When

- Borrower debt must be represented as principal plus per-account index snapshots
- Losses must be assigned to specific tranches or lenders
- Share conversions cannot tolerate rounding differences

## How It Works

Convert between assets and shares against market totals:

```solidity
function toShares(uint256 assets, uint256 totalAssets, uint256 totalShares) internal pure returns (uint256) {
    return assets * (totalShares + VIRTUAL_SHARES) / (totalAssets + VIRTUAL_ASSETS);
}

function toAssets(uint256 shares, uint256 totalAssets, uint256 totalShares) internal pure returns (uint256) {
    return shares * (totalAssets + VIRTUAL_ASSETS) / (totalShares + VIRTUAL_SHARES);
}
```

Supply and borrow sides can each have their own total assets and total shares. Accrual updates total assets, while positions keep their share counts.

A debt-distribution system can use the same share idea with signed
`valuePerShare` changes. Market debt flows into pool debt, pool debt flows into
vault debt, and account debt is lazily consolidated only when the relevant
market, pool, vault, or account interacts.

## Key Points

- Define rounding direction per action: user-favoring and protocol-favoring paths should be explicit.
- Use virtual offsets or minimum liquidity to avoid first-share inflation.
- Keep total assets and total shares internally consistent after interest, repayment, liquidation, and bad debt.
- Do not mix share-based positions with principal-index positions without a clear conversion boundary.
- Test asset/share round trips at zero, dust, and high utilization.
- For borrow shares, debt views and new borrows should round up, partial repayments can round share burn down, and full repayment should burn all remaining shares so dust debt does not survive.
- For signed debt distributions, checkpoint each layer before moving collateral,
  changing pool weights, issuing debt, or reporting withdrawable credit.

## Source Evidence

- Morpho Blue stores separate supply and borrow shares, uses virtual offsets in conversion math, applies explicit directional rounding, and formally specifies conservative asset accounting rules.
- Alpha Homora V2 computes borrow balances with ceiling division, mints borrow shares with ceiling division, caps repayment to old debt, floors partial share reduction, and burns all remaining shares on full repayment in `/private/tmp/defillama-source/AlphaFinanceLab__alpha-homora-v2-contract/contracts/HomoraBank.sol`.
- Fraxlend `VaultAccount` stores `amount` and `shares` totals and converts with explicit rounding direction for asset and borrow accounting in `/private/tmp/defillama-source/FraxFinance__fraxlend/src/contracts/libraries/VaultAccount.sol`.
- Synthetix V3 distributes signed debt per share through market, pool, vault, and
  account layers using lazy consolidation in `/private/tmp/defillama-source/synthetixio__synthetix-v3/protocol/synthetix/contracts/storage/Distribution.sol:9-18`,
  `/private/tmp/defillama-source/synthetixio__synthetix-v3/protocol/synthetix/contracts/storage/Pool.sol:186-249`,
  and `/private/tmp/defillama-source/synthetixio__synthetix-v3/protocol/synthetix/contracts/storage/Market.sol:370-461`.

## Related Patterns

- [Scaled Balance Token Accounting](./pattern-scaled-balance-token-accounting.md)
- [Virtual Share Offset](../vaults/pattern-virtual-share-offset.md)
- [Explicit Bad-Debt Realization](./pattern-explicit-bad-debt-realization.md)
