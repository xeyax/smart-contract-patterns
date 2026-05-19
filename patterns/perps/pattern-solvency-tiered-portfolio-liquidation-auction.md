# Solvency-Tiered Portfolio Liquidation Auction

> Liquidate a whole derivative portfolio through Dutch-auction modes that distinguish solvent and insolvent accounts.

## Metadata

| Property | Value |
|----------|-------|
| Category | perps |
| Tags | perps, options, liquidation, auction, insolvency |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Accounts hold multi-asset derivative portfolios rather than one isolated position
- Solvent and insolvent accounts need different liquidation pricing or fill limits
- A liquidator should take a bounded proportion of the portfolio
- The auction can guard price, trade id, and risk-scenario updates

## Avoid When

- Positions can be liquidated independently without portfolio effects
- The protocol lacks a reliable post-fill solvency check
- Auction fills can ignore stale oracle or stale risk scenario state
- Insolvent losses have no backstop or socialization path

## Trade-offs

**Pros:**
- Preserves portfolio relationships during liquidation
- Lets solvent accounts receive less punitive pricing than insolvent accounts
- Makes backstop and socialized-loss transitions explicit

**Cons:**
- Whole-portfolio fills are complex to price and test
- Dutch-auction parameters strongly affect liquidator incentives
- Insolvent mode needs clear loss containment and accounting

## How It Works

When an account breaches maintenance margin, start or read a Dutch auction over a
portfolio fill. Solvent mode caps fill proportion and price progression more
conservatively. Insolvent mode can use different discounts and backstop logic,
then updates worst-risk scenarios after the fill.

```solidity
function fillLiquidation(uint256 accountId, Fill calldata fill) external {
    AuctionMode mode = _solvencyMode(accountId);
    AuctionTerms memory terms = _terms(accountId, mode, block.timestamp);

    require(fill.tradeId == terms.tradeId, "trade id");
    require(fill.proportion <= terms.maxProportion, "too much");
    require(_priceOk(fill, terms), "price");

    _transferPortfolioSlice(accountId, msg.sender, fill);
    _updateWorstScenario(accountId);
    _resolveBackstopIfInsolvent(accountId);
}
```

## Implementation

- Separate solvent and insolvent auction modes and parameters.
- Cap fill proportion per auction or per fill.
- Bind fill prices to trade id, auction start, and current oracle/risk state.
- Update account risk scenarios after each fill.
- Define backstop exhaustion and socialized-loss behavior.
- Test solvent fills, insolvent fills, stale trade ids, price guards, partial fills, and backstop exhaustion.

## Source Evidence

- Derive V2 Dutch auctions switch between solvent and insolvent liquidation modes, cap fill proportion, guard price and trade ids, and update risk scenarios in `/private/tmp/defillama-source/derivexyz__v2-core/src/liquidation/DutchAuction.sol`.
- Derive V2 tests solvent and insolvent auction behavior in `test/auction/unit-tests/SolventAuction.t.sol` and `test/auction/unit-tests/InsolventAuction.t.sol`.

## Real-World Examples

- Derive V2 liquidates derivative portfolios through solvency-tiered Dutch auctions.

## Related Patterns

- [Scenario-Shocked Portfolio Margin](./pattern-scenario-shocked-portfolio-margin.md)
- [Progressive Liquidation State Machine](./pattern-progressive-liquidation-state-machine.md)
- [Explicit Bad Debt Realization](../lending/pattern-explicit-bad-debt-realization.md)

## References

- Derive V2 liquidation auction source.
