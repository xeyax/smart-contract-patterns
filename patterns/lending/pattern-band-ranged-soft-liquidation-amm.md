# Band-Ranged Soft Liquidation AMM

> Liquidate collateral gradually by placing it across oracle-priced AMM bands before hard liquidation is needed.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | cdp, liquidation, amm, bands, soft-liquidation |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A collateralized debt protocol wants smoother liquidation than a single auction or seizure point
- Collateral can be converted against debt asset through protocol-owned AMM bands
- Oracle price movement should gradually transform collateral into debt repayment liquidity
- Hard liquidation remains available for unhealthy residual positions

## Avoid When

- The collateral market is too illiquid or manipulable for AMM-based liquidation
- Oracle price and AMM band math cannot be kept coherent
- Users need simple all-or-nothing liquidation semantics

## Trade-offs

**Pros:**
- Reduces cliff liquidation pressure
- Lets positions deleverage progressively as prices move
- Can make liquidation proceeds more continuous and predictable

**Cons:**
- Oracle, band, and health math are tightly coupled
- Positions can be partially liquidated for long periods
- Band traversal and rounding need heavy invariant and fuzz testing

## How It Works

When a borrower opens a loan, collateral is distributed across a price band range.
As the oracle price moves through bands, the AMM converts collateral into the
debt asset. Health checks decide whether the remaining position requires hard
liquidation.

```vyper
def create_loan(collateral, debt, n_bands):
    lower, upper = _bands_for_debt(collateral, debt, n_bands)
    amm.deposit_range(msg.sender, collateral, lower, upper)
    debt_token.mint(msg.sender, debt)

def liquidate(user):
    assert self._health(user) < 0
    amount = self.tokens_to_liquidate(user)
    self._repay_and_collect_collateral(user, amount)
```

## Implementation

- Keep oracle price, band indexing, and health calculations in one audited model.
- Test band crossing, empty bands, partial liquidation, full liquidation, and oracle jumps.
- Define when soft-liquidated users can add collateral, repay, or withdraw.
- Keep hard liquidation as a fallback for unhealthy residual debt.
- Bound gas for traversing bands or expose resumable operations.

## Source Evidence

- Curve crvUSD implements band-based liquidation in [`curve_stablecoin/AMM.vy`](https://github.com/curvefi/curve-stablecoin/blob/8a98f2043d3f4f2b0eb14c24e89d21df32e4bba6/curve_stablecoin/AMM.vy).
- crvUSD controller loan and liquidation logic lives in [`curve_stablecoin/controller.vy`](https://github.com/curvefi/curve-stablecoin/blob/8a98f2043d3f4f2b0eb14c24e89d21df32e4bba6/curve_stablecoin/controller.vy) through `create_loan`, `_health`, `liquidate`, and `tokens_to_liquidate`.
- Curve includes stable-borrow tests under `tests/stableborrow/` and stateful fuzz tests in `tests/fuzz/stateful/test_controller_stateful.py`.

## Real-World Examples

- Curve crvUSD LLAMMA uses oracle-priced bands for soft liquidation.

## Related Patterns

- [Risk-Priority Liquidation Sequencing](./pattern-risk-priority-liquidation-sequencing.md)
- [Resettable Dutch Liquidation Auction](./pattern-resettable-dutch-liquidation-auction.md)
- [Price Manipulation Risk](../oracles/risk-price-manipulation.md)

## References

- Curve crvUSD AMM and controller contracts.
