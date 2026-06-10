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

## Trade-offs

**Pros:**
- Interest accrues globally through one index update instead of iterating every account, keeping accrual gas O(1) in holder count.
- `balanceOf` reflects current accrued value, so integrators see live balances without calling an accrual function first.
- Lazy per-user updates keep mint/burn/transfer cheap: one scaled-amount conversion per touched account.
- Battle-tested shape (Aave V2/V3 and derivatives), so auditors and integrators know the invariants to check.

**Cons:**
- Every state-changing path must accrue the index first; a single missed accrual lets users mint or burn at a stale rate.
- Rounding in scaled conversions is a persistent leak surface — mint/burn residual direction must be pinned or dust accumulates as free value.
- Index-multiplied balances confuse naive integrators: transfers move scaled units, `totalSupply` drifts continuously, and snapshot/vote tooling built for static balances misbehaves.
- A decreasing index (loss socialization) is outside the basic model and needs explicit design, or losses silently corrupt accounting.
- Transferable interest-bearing balances must hook into risk checks, coupling token transfer logic to pool health validation.

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
- Aave V2 uses the same scaled-balance shape for aTokens and variable debt tokens: mint and burn convert through liquidity or variable-borrow indexes, while balance views multiply scaled balances by normalized income or debt in [`contracts/protocol/tokenization`](https://github.com/aave/protocol-v2/blob/ce53c4a8c8620125063168620eba0a8a92854eb8/contracts/protocol/tokenization).
- Zest Protocol zTokens lazily cumulate balances from liquidity indexes and tests zToken upgrades and balance carry-forward in [`onchain/contracts/borrow/production/ztoken`](https://github.com/Zest-Protocol/zest-contracts/blob/3564bc38906e464ec4de774122bb9bbaee20ddc6/onchain/contracts/borrow/production/ztoken) and `onchain/tests/borrow/upgrade-z-token-v2.test.ts`.
- BendDAO bTokens and debt tokens mint and burn scaled balances against reserve liquidity and variable-borrow indexes, while balance views multiply by normalized income or debt in [`contracts/protocol/BToken.sol`](https://github.com/BendDAO/bend-lending-protocol/blob/81c90c06373bd6cc616ed0d0712fe382cad56548/contracts/protocol/BToken.sol) and [`contracts/protocol/DebtToken.sol`](https://github.com/BendDAO/bend-lending-protocol/blob/81c90c06373bd6cc616ed0d0712fe382cad56548/contracts/protocol/DebtToken.sol).

## Related Patterns

- [Lazy Borrow Index](./pattern-lazy-borrow-index.md)
- [Share-Denominated Lending Accounting](./pattern-share-denominated-lending-accounting.md)
- [Lending Accounting Freshness Requirements](./req-lending-accounting-freshness.md)
