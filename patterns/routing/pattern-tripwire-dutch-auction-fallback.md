# Tripwire Dutch Auction Fallback

> Disable risky Dutch-auction routes after anomalous fills and force future trades through a safer fallback until governance reviews the route.

## Metadata

| Property | Value |
|----------|-------|
| Category | routing |
| Tags | routing, auction, dutch-auction, fallback, oracle |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A protocol uses Dutch auctions for rebalancing, revenue, or recollateralization
- Auction prices depend on oracle ranges that can be wrong or manipulated
- A slower batch auction or governance-reviewed route is available as fallback
- An anomalous fill can be detected by the auction contract

## Avoid When

- There is no alternative execution venue
- The anomaly signal is too noisy and would halt normal trading constantly
- Governance cannot review and re-enable disabled routes
- The auction is only for user-directed swaps with user slippage bounds

## Trade-offs

**Pros:**
- Limits repeated loss after the first suspicious Dutch fill
- Makes route disablement automatic and observable
- Keeps a fallback path for critical maintenance trades

**Cons:**
- False positives can push trades to slower or more expensive venues
- Requires careful anomaly definition
- Governance re-enable authority becomes important

## How It Works

The auction reports a violation when it clears in a price region that should be economically implausible under honest oracle inputs:

```solidity
function settle() external {
    if (_clearedInTripwirePhase()) {
        broker.reportViolation(sellToken, buyToken);
    }
    _settleTrade();
}

function reportViolation(address sell, address buy) external onlyKnownTrade {
    dutchDisabled[sell] = true;
    dutchDisabled[buy] = true;
}
```

Future trade requests for implicated tokens use the fallback venue until governance explicitly re-enables Dutch execution.

## Implementation

```solidity
function openTrade(TradeRequest memory req) external returns (address trade) {
    if (dutchDisabled[address(req.sell)] || dutchDisabled[address(req.buy)]) {
        return _openBatchAuction(req);
    }
    return _openDutchAuction(req);
}
```

### Key Points

- Define the tripwire phase from conservative price bounds, not from operator discretion.
- Disable both sell and buy assets when either side could have been manipulated.
- Allow only recognized auction instances to report violations.
- Emit route disable and re-enable events.
- Test that fallback remains available after tripwire activation.

## Source Evidence

- Reserve Protocol Dutch trades can report violations; `Broker.reportViolation` disables future Dutch auctions for implicated tokens and future trade openings can use batch auctions in [`contracts/p1/Broker.sol`](https://github.com/reserve-protocol/protocol/blob/9cda9d89c871e70886fc4453f94fc6aa889445df/contracts/p1/Broker.sol) and `contracts/plugins/trading/DutchTrade.sol`.
- Reserve recollateralization and broker tests cover Dutch auction disablement and fallback behavior in [`test`](https://github.com/reserve-protocol/protocol/blob/9cda9d89c871e70886fc4453f94fc6aa889445df/test).

## Real-World Examples

- Reserve Protocol - Dutch auction tripwire disables risky token pairs and falls back to batch auctions.

## Related Patterns

- [Bounded Rebalance Auction](../vaults/pattern-bounded-rebalance-auction.md)
- [Resettable Dutch Liquidation Auction](../lending/pattern-resettable-dutch-liquidation-auction.md)
- [Oracle Reliability Requirements](../oracles/req-oracle-reliability.md)

## References

- See Source Evidence.
