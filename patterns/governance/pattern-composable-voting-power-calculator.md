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
