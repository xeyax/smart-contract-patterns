# Projected Versus Realized NAV Split

> Expose continuous target accrual for vault previews while keeping realized NAV separate until discrete rewards or losses are actually accounted.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, nav, accounting, accrual, tranches |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Vault yield arrives as discrete reward, coupon, or strategy accounting events
- Users need previews between realized accounting events
- Senior and junior tranches accrue against target rates or indexes
- The protocol must not treat projected yield as spendable cash

## Avoid When

- NAV can be measured continuously from liquid on-chain balances
- Projected accrual can be arbitraged by temporary TVL changes
- Accounting updates can be sandwiched without minimum-liquidity or cooldown guards
- Users cannot distinguish estimated previews from realized settlement values

## Trade-offs

**Pros:**
- Gives smoother previews between discrete reward arrivals
- Separates expected accrual from realized assets
- Makes realized true-up events explicit and auditable

**Cons:**
- More complex than a single `totalAssets()` value
- Temporary TVL changes can distort projected accrual if updates are not guarded
- Requires clear UI and integration language around estimates

## How It Works

Maintain two accounting surfaces:

- projected NAV, derived from the previous realized NAV, elapsed time, target rates, and tranche indexes
- realized NAV, updated only when rewards, losses, or strategy reports are actually accounted

```solidity
function projectedNav() public view returns (uint256) {
    uint256 elapsed = block.timestamp - lastRealizedAt;
    return lastRealizedNav + accrueTarget(lastRealizedNav, targetRate, elapsed);
}

function accountReward(uint256 reward) external onlyAccountant {
    uint256 projected = projectedNav();
    uint256 realized = strategy.realizedNav() + reward;

    _trueUpTranches(projected, realized);
    lastRealizedNav = realized;
    lastRealizedAt = block.timestamp;
}
```

Previews may use projected NAV, but settlement, fee extraction, and loss realization should name whether they consume projected or realized values.

## Implementation

### Key Points

- Store the last realized NAV and timestamp separately from target accrual indexes.
- Label preview values as projected when rewards have not been realized.
- True up projected accrual against realized rewards or losses in one accounting step.
- Guard accounting updates against temporary TVL changes and same-block sandwiching.
- Test no-reward accrual, reward true-up, loss true-up, and tranche boundary cases.
- Add minimum share price, minimum supply, or pause thresholds for extreme tranche states.

## Source Evidence

- Strata `DiscreteAccounting` stores target NAV indexes and separate projected and real junior NAV in `/private/tmp/defillama-source/Strata-Markets_contracts/contracts/tranches/DiscreteAccounting.sol`.
- Strata tests no-reward projected values followed by realized reward true-up in `/private/tmp/defillama-source/Strata-Markets_contracts/test/tranches/accounting/DiscreteAccounting.spec.ts`.
- Strata PoC tests under `/private/tmp/defillama-source/Strata-Markets_contracts/test/PoC` show that APR/accounting updates and low junior prices can create timing-sensitive outcomes if projected accrual is not guarded.

## Real-World Examples

- Strata Markets uses projected accounting between discrete reward accounting events for tranched vault previews.

## Related Patterns

- [Rate-Bounded NAV Report](./pattern-rate-bounded-nav-report.md)
- [Coverage-Ratio Gated Tranche Exits](./pattern-coverage-ratio-gated-tranche-exits.md)
- [Tiered Loss Waterfall Requirements](./req-tiered-loss-waterfall.md)

## References

- See Source Evidence.
