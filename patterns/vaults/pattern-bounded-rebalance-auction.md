# Bounded Rebalance Auction

> Let managers rebalance basket vaults through auctions while constraining assets, weights, prices, duration, and later parameter changes.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, rebalance, auction, basket, manager, allowlist |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A vault holds a managed basket or index of multiple assets
- A manager needs discretion to rebalance composition over time
- Direct manager swaps would grant too much pricing power
- Non-curated assets may need to be unwound safely

## Avoid When

- The vault composition is fully immutable
- Rebalancing can be expressed as simple proportional deposit/withdraw flows
- There is no reliable pricing or auction settlement mechanism

## Trade-offs

**Pros:**
- Preserves manager flexibility while bounding abuse
- External bidders can compete on execution
- Sell-only handling lets the vault unwind non-curated assets
- Auction constraints are easier to audit than arbitrary swap calldata

**Cons:**
- More state and lifecycle complexity
- Bad bounds can still create poor execution
- Requires monitoring while auctions are open

## How It Works

A rebalance defines allowed tokens, target weights, price ranges, limits, and expiry. Managers can open an auction only inside those bounds, and later changes can only narrow risk.

```solidity
function startRebalance(Rebalance calldata r) external onlyManager {
    _requireNoDuplicateTokens(r.tokens);
    _requireAllowedOrSellOnly(r.tokens, r.targetWeights);
    _requireWeightRanges(r.targetWeights, r.minWeights, r.maxWeights);
    _requirePriceRanges(r.prices);
    _requireTtl(r.endTime);

    activeRebalance = r;
}

function openAuction(Auction calldata a) external onlyManager {
    _requireWithinActiveRebalance(a);
    _requireOnlyNarrowing(a);
    _startAuction(a);
}
```

## Key Points

- Validate token allowlists before setting positive target weights.
- Permit non-allowlisted tokens only with zero target weight so they can be sold down.
- Bound auction length, price ranges, per-token limits, and duplicate tokens.
- Let later manager actions narrow ranges, not widen them, unless governance restarts the rebalance.
- Expose active external fill or auction state for integrators that read NAV or previews.

## Source Evidence

- Reserve Index DTF validates rebalance allowlists, TTLs, limits, duplicate tokens, weight ranges, and price ranges before opening auctions.
- Reserve permits non-allowlisted tokens only when their target weights are zero, allowing sell-down without new exposure.

## Related Patterns

- [Proportional Deposit/Withdrawal](./pattern-proportional-deposit.md) - oracle-free entry/exit for multi-asset vaults
- [Delta NAV Share Accounting](./pattern-delta-nav.md) - NAV accounting for managed baskets
- [Missing Slippage Protection](../../ANTIPATTERNS.md#missing-slippage-protection) - user and manager execution bounds
