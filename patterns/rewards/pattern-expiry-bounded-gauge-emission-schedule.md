# Expiry-Bounded Gauge Emission Schedule

> Schedule gauge emissions for a fixed-maturity market only within the market's active lifetime and under per-second caps.

## Metadata

| Property | Value |
|----------|-------|
| Category | rewards |
| Tags | rewards, gauge, emissions, expiry, fixed-maturity |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Liquidity incentives target markets with fixed expiry
- Emission rates are set by governance or an operator
- Reward accrual should be lazy but bounded by configured start/end times
- The market should not receive incentives after it can no longer trade normally

## Avoid When

- The pool has no maturity or expiry boundary
- Excess emissions need redistribution to other gauges
- Admins can set arbitrary extreme rates without caps
- Users need reward guarantees independent of gauge whitelisting

## Trade-offs

**Pros:**
- Prevents emissions from leaking into expired markets
- Caps reward rate risk per market
- Keeps accrual lazy and cheap for inactive markets

**Cons:**
- Requires reliable market expiry metadata
- Admin cap and schedule validation become economic security boundaries
- Does not solve how unused rewards should be redistributed

## How It Works

Governance whitelists the market, caps its rate, and sets an incentive end before market expiry:

```solidity
function setEmission(address market, uint128 rate, uint32 end) external onlyGaugeAdmin {
    require(isWhitelisted[market], "market");
    require(rate <= maxRate[market], "rate");
    require(end <= marketExpiry[market], "expiry");
    _accrue(market);
    emissionRate[market] = rate;
    incentiveEndsAt[market] = end;
}
```

The gauge accrues lazily up to `min(block.timestamp, incentiveEndsAt)`.

## Implementation

### Key Points
- Read or store market expiry before accepting an emission schedule.
- Cap emissions per market and per second.
- Accrue old rewards before changing rates or end times.
- Decide whether post-expiry unallocated rewards remain idle, return to treasury, or require manual recovery.
- Use typed `require` checks for admin configuration rather than assertion-only validation.
- Test schedule changes around expiry, zero rates, over-cap rates, and delayed accrual.

## Source Evidence

- Pendle V2 gauge control whitelists markets, caps per-second emissions, accrues rewards lazily, and requires incentive periods to end before market expiry in `/private/tmp/defillama-source/pendle-finance__pendle-core-v2-public/contracts/LiquidityMining/GaugeController/PendleGaugeControllerUpg.sol`.

## Real-World Examples

- Pendle V2 uses expiry-aware gauge emissions for fixed-yield markets.

## Related Patterns

- [Lazy Reward Index](./pattern-lazy-reward-index.md)
- [Capped Gauge Emission Redistribution](./pattern-capped-gauge-emission-redistribution.md)
- [Reward Token Accrual DoS](./risk-reward-token-accrual-dos.md)
