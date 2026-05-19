# Resettable Dutch Liquidation Auction

> Sell liquidated collateral through a descending-price auction that can be reset when it becomes stale or too far below its starting price.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, liquidation, auction, dutch-auction, keeper |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Collateral is sold after liquidation rather than seized directly by the liquidator
- Price discovery should happen through a descending auction
- Auctions can become stale or mispriced during volatility
- Keepers need incentives to reset or take auctions

## Avoid When

- Collateral is highly liquid and direct liquidation is simpler
- Oracle price cannot provide a safe starting anchor
- Keeper incentives can exceed expected auction value

## How It Works

Start the auction above the oracle value, decay price over time, and allow reset when stale:

```solidity
function price(uint256 id) public view returns (uint256) {
    Auction memory a = auctions[id];
    return decay(a.startPrice, block.timestamp - a.startTime);
}

function redo(uint256 id) external {
    Auction storage a = auctions[id];
    require(block.timestamp > a.startTime + tail || price(id) < a.startPrice * cusp / WAD, "not stale");
    a.startPrice = oraclePrice() * buffer / WAD;
    a.startTime = block.timestamp;
    _payKeeperIncentive(msg.sender);
}
```

Buyers submit a maximum acceptable price or cost bound when taking collateral.

## Key Points

- Buffer the start price above oracle value to avoid immediate underpricing.
- Let buyers set max price or max cost bounds.
- Reset by time elapsed and price decline thresholds.
- Bound keeper incentives and disable auction functions by staged breaker levels.
- Account for dust and active liquidation caps before starting auctions.
- Throttle active liquidation debt globally and per collateral.
- Size partial liquidations so they do not leave uneconomic leftover debt or collateral.
- Expose breaker levels that can separately stop new auctions, auction resets, and auction takes.

## Source Evidence

- Sky/Maker DSS `Clipper` auctions use feed-buffered start prices, descending price curves, buyer max-price bounds, stale-auction reset by time or price decline, keeper incentives, and breaker levels.
- Lista CDP liquidation code throttles active liquidation debt globally and per collateral, sizes auctions around dust constraints, and exposes staged breakers for kicks, resets, and takes.

## Related Patterns

- [Dust-Aware Liquidation Cap](./pattern-dust-aware-liquidation-cap.md)
- [Bounded Rebalance Auction](../vaults/pattern-bounded-rebalance-auction.md)
- [Protocol-Absorbed Liquidation Inventory](./pattern-protocol-absorbed-liquidation-inventory.md)
