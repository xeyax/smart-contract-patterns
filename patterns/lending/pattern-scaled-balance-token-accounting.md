# Scaled Balance Token Accounting

> Store token balances scaled by a liquidity or debt index so interest accrues globally while user balances update lazily.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, accounting, scaled-balance, index, atoken, debt-token |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- A lending protocol represents supplied or borrowed positions as transferable or account-bound tokens
- Interest accrues continuously through a market index
- Updating every account on every accrual would be impossible
- Balance views should reflect current accrued value

## Avoid When

- Balances must be fixed principal amounts
- The index can decrease without explicitly handling losses
- Rounding direction cannot be bounded for mint, burn, and transfer

## How It Works

Store scaled units internally and convert through the current index:

```solidity
function balanceOf(address user) public view returns (uint256) {
    return scaledBalance[user] * liquidityIndex / RAY;
}

function mint(address user, uint256 assets) external onlyPool {
    uint256 scaled = assets * RAY / liquidityIndex;
    scaledBalance[user] += scaled;
    scaledTotalSupply += scaled;
}
```

Debt tokens use the same shape with a borrow index. The index update belongs to the market or pool, not to every token holder.

## Key Points

- Accrue the market index before minting, burning, liquidating, or transferring interest-bearing balances.
- Define rounding direction for scaled mint/burn so small residuals do not create free value.
- If the index can decrease because of losses, document how balances absorb the loss.
- Keep raw scaled totals and current asset totals reconcilable in tests.
- Link transfer hooks to risk checks when interest-bearing balances are transferable collateral.

## Source Evidence

- Aave V3 represents supplied and borrowed positions through scaled balances multiplied by liquidity or borrow indexes, allowing global accrual without per-user iteration.
- Aave V2 uses the same scaled-balance shape for aTokens and variable debt tokens: mint and burn convert through liquidity or variable-borrow indexes, while balance views multiply scaled balances by normalized income or debt in `/private/tmp/defillama-source/aave__protocol-v2/contracts/protocol/tokenization`.
- Zest Protocol zTokens lazily cumulate balances from liquidity indexes and tests zToken upgrades and balance carry-forward in `/private/tmp/defillama-source/Zest-Protocol__zest-contracts/onchain/contracts/borrow/production/ztoken` and `onchain/tests/borrow/upgrade-z-token-v2.test.ts`.

## Related Patterns

- [Lazy Borrow Index](./pattern-lazy-borrow-index.md)
- [Share-Denominated Lending Accounting](./pattern-share-denominated-lending-accounting.md)
- [Lending Accounting Freshness Requirements](./req-lending-accounting-freshness.md)
