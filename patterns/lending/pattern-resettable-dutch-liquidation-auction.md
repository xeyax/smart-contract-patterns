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

## Trade-offs

**Pros:**
- Descending price gives market-driven price discovery for collateral that is too illiquid for fixed-discount direct seizure.
- Reset on staleness or excessive decline prevents auctions from settling at deeply underpriced levels during volatility.
- Buyer max-price/max-cost bounds and partial fills let small takers participate without atomically funding the whole lot.
- Staged breakers can separately halt kicks, resets, and takes, giving fine-grained incident response.

**Cons:**
- Settlement latency: debt stays open while the price decays, and each reset restarts the clock, extending protocol exposure during exactly the volatile periods that trigger resets.
- Keeper incentive design is fragile — incentives can exceed auction value, invite self-kicking or reset farming, and need explicit bounding.
- Start price still anchors to an oracle, so the pattern does not remove oracle risk, only converts it into a buffered starting point.
- Decay curves, reset thresholds, two-sided block scaling, and bond reward/penalty paths multiply the state space; partial-fill rounding direction is an easy place to leak collateral.
- Liveness depends on competitive keeper and taker participation; on quiet chains or for thin collateral, auctions can decay to near-zero before anyone takes.

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

### Two-Sided Block-Scaled Fill Variant

A liquidation auction can scale the lot side and bid side separately over block
age. For example, the lot amount grows during the first window to attract fills,
then the bid side decreases later as the auction ages:

```rust
let elapsed = current_block - auction.start_block;
let lot = scale_lot_up(initial_lot, elapsed.min(LOT_RAMP_BLOCKS));
let bid = scale_bid_down(initial_bid, elapsed.saturating_sub(LOT_RAMP_BLOCKS));
```

Partial fills need explicit rounding direction. Round bids up so the buyer pays
at least the required amount, and round lots down so the auction does not release
more collateral than the fill earned.

### Bonded Neutral-Price Variant

Some lending books let a kicker start an auction only by posting a bond. The
auction references a neutral price, forbids same-block take after kick, descends
through configured phases, and rewards or penalizes the kicker bond based on
whether the auction helped settle risky debt.

## Key Points

- Buffer the start price above oracle value to avoid immediate underpricing.
- Let buyers set max price or max cost bounds.
- Reset by time elapsed and price decline thresholds.
- Bound keeper incentives and disable auction functions by staged breaker levels.
- Account for dust and active liquidation caps before starting auctions.
- Throttle active liquidation debt globally and per collateral.
- Size partial liquidations so they do not leave uneconomic leftover debt or collateral.
- Expose breaker levels that can separately stop new auctions, auction resets, and auction takes.
- For two-sided scaling, test each block-age phase, partial fills, and one-unit dust boundaries with the intended rounding directions.
- For bonded auctions, test kicker bond reward and penalty paths, neutral-price
  calculation, same-block take rejection, and each descending-price phase.

## Source Evidence

- Sky/Maker DSS `Clipper` auctions use feed-buffered start prices, descending price curves, buyer max-price bounds, stale-auction reset by time or price decline, keeper incentives, and breaker levels.
- Lista CDP liquidation code throttles active liquidation debt globally and per collateral, sizes auctions around dust constraints, and exposes staged breakers for kicks, resets, and takes.
- Blend V2 auction fill scales lots upward and bids downward by block age in [`pool/src/auctions/auction.rs`](https://github.com/blend-capital/blend-contracts-v2/blob/ba22b487b2c5057a4ecc28b05b5193c28e4bd117/pool/src/auctions/auction.rs), with tests for block-age phases, partial fills, rounding direction, and dust.
- Ajna kicks auctions with a bond, computes neutral/reference price, rejects
  same-block takes, and applies phase-based descending auction price plus kicker
  reward/penalty logic in [`src/libraries/external/KickerActions.sol:307-384`](https://github.com/ajna-finance/ajna-core/blob/0f59e78031af76d62ad575c18405eb325b28849f/src/libraries/external/KickerActions.sol#L307-L384),
  [`src/libraries/helpers/PoolHelper.sol:417-492`](https://github.com/ajna-finance/ajna-core/blob/0f59e78031af76d62ad575c18405eb325b28849f/src/libraries/helpers/PoolHelper.sol#L417-L492),
  and [`src/libraries/external/TakerActions.sol:684-786`](https://github.com/ajna-finance/ajna-core/blob/0f59e78031af76d62ad575c18405eb325b28849f/src/libraries/external/TakerActions.sol#L684-L786).

## Related Patterns

- [Dust-Aware Liquidation Cap](./pattern-dust-aware-liquidation-cap.md)
- [Bounded Rebalance Auction](../vaults/pattern-bounded-rebalance-auction.md)
- [Protocol-Absorbed Liquidation Inventory](./pattern-protocol-absorbed-liquidation-inventory.md)
