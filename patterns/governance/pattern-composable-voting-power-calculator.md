# Composable Voting-Power Calculator

> Compute voting power from normalized token, vault, price, and weight components behind explicit calculator modules.

## Metadata

| Property | Value |
|----------|-------|
| Category | governance |
| Tags | governance, voting-power, oracle, vault, composition |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Voting power depends on several tokens, vault shares, or restaked positions
- Components use different decimals or exchange-rate sources
- Governance wants reusable calculators for multiple networks or operator sets
- A zero or stale component should have explicit quorum consequences

## Avoid When

- Voting power can be a simple token balance snapshot
- Price sources are not reliable enough for validator-set fairness
- The calculator would be too expensive for on-chain critical paths
- Component weights are subjective and frequently changed without delay

## Trade-offs

**Pros:**
- One calculator interface is reusable across networks and operator sets instead of bespoke per-deployment power logic.
- Up-front decimal and exchange-rate normalization removes a whole class of weighting-mismatch bugs.
- An explicit stale-price policy (revert, zero, or freeze) makes quorum consequences predictable instead of accidental.
- Timelocked weights, vault additions, and calculator replacement resist governance capture by quiet reweighting.

**Cons:**
- Per-component balance and price reads make power queries gas-expensive; unbounded component lists can DoS on-chain critical paths.
- Validator-set fairness inherits the oracle trust and staleness risk of every component feed.
- Fail-closed staleness handling can zero a component's power and silently shift quorum and control.
- Composition bugs — duplicate components, weight drift, rounding across decimals — are subtle and need broad property testing.
- The calculator itself is replaceable infrastructure, making its upgrade path a governance attack surface in its own right.

## How It Works

Normalize every component to one precision and compose weights through a calculator interface:

```solidity
function votingPower(address operator) external view returns (uint256 power) {
    for (uint256 i; i < components.length; i++) {
        Component memory c = components[i];
        uint256 balance = c.source.balanceOf(operator);
        uint256 price = c.priceFeed.price();
        power += _normalize(balance, c.decimals) * price * c.weightBps / BPS;
    }
}
```

The calculator should fail closed or apply a documented conservative value when a component price is stale or unavailable.

## Key Points

- Normalize token and vault decimals before weighting.
- Keep component lists bounded or paginated for on-chain use.
- Define whether stale prices revert, zero the component, or freeze prior power.
- Timelock component weights, vault additions, and calculator replacement.
- Test composition across decimals, zero balances, stale prices, and duplicate components.

## Source Evidence

- Symbiotic Relay composes token, vault, price-feed, and weighted calculator modules for validator voting power, including tests for decimal normalization and stale-price behavior.

## Related Patterns

- [Oracle Staleness Risk](../oracles/risk-oracle-staleness.md)
- [Uncapped Chain Voting-Power Concentration](./risk-uncapped-chain-voting-power-concentration.md)
