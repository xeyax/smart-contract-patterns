# Paid Early Oracle Update Liquidation

> Delay ordinary oracle reads while allowing liquidation callers to pay for fresh rounds and share the resulting opportunity with the protocol.

## Metadata

| Property | Value |
|----------|-------|
| Category | oracles |
| Tags | oracle, liquidation, oev, chainlink, freshness |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Oracle extractable value exists around liquidation price updates
- Ordinary protocol reads can tolerate a bounded delayed price
- Liquidation callers can supply signed fresh oracle data or pay update costs
- The protocol can share liquidation surplus or fees from early access

## Avoid When

- Users expect `latestRoundData` to always mean the newest public round
- The delayed read path is undocumented or used by unrelated value transfers
- The wrapper cannot prove update authenticity and freshness
- Liquidation profitability is not bounded by health and close-factor checks

## Trade-offs

**Pros:**
- Captures some oracle-update value for the protocol instead of only searchers
- Keeps ordinary reads stable while preserving fresh liquidation execution
- Makes early-update economics explicit

**Cons:**
- Changes the semantics of common oracle interfaces
- Adds a privileged liquidation path that must be documented clearly
- Misconfigured delays can create stale-state risk for ordinary users

## How It Works

The wrapper exposes delayed prices for ordinary reads. A liquidation helper can
submit fresh update data, run the liquidation against the fresh value, and split
profit or fees:

```solidity
function latestRoundData() external view returns (Round memory) {
    return delayedRound;
}

function liquidateWithUpdate(Update calldata update, Liquidation calldata liq) external {
    Round memory fresh = _verifyFreshRound(update);
    _setTemporaryLiquidationPrice(fresh);
    uint256 profit = lendingMarket.liquidate(liq);
    _shareOev(profit, msg.sender, protocolTreasury);
    _clearTemporaryPrice();
}
```

## Implementation

### Key Points

- Document that ordinary reads are intentionally delayed.
- Bind submitted updates to the feed, round id, timestamp, and signer/update-data domain.
- Restrict fresh-price use to liquidation or other explicitly listed paths.
- Keep liquidation health checks and close factors independent of OEV accounting.
- Test stale ordinary reads, fresh liquidation updates, bad update data, profit sharing, and read-path compatibility.

## Source Evidence

- Moonwell documents OEV-delayed reads and liquidation-wrapper behavior in [`docs/OEV.md`](https://github.com/moonwell-fi/moonwell-contracts-v2/blob/9ed6ad9b692a924213656926baf5637875b0e646/docs/OEV.md).
- Moonwell Chainlink OEV wrapper exposes delayed ordinary reads and fresh liquidation update paths in [`src/oracles/ChainlinkOEVWrapper.sol`](https://github.com/moonwell-fi/moonwell-contracts-v2/blob/9ed6ad9b692a924213656926baf5637875b0e646/src/oracles/ChainlinkOEVWrapper.sol).
- Moonwell Morpho OEV wrapper extends the same idea in [`src/oracles/ChainlinkOEVMorphoWrapper.sol`](https://github.com/moonwell-fi/moonwell-contracts-v2/blob/9ed6ad9b692a924213656926baf5637875b0e646/src/oracles/ChainlinkOEVMorphoWrapper.sol).

## Real-World Examples

- Moonwell - Chainlink OEV wrappers delay ordinary reads and expose paid early liquidation updates.

## Related Patterns

- [Chainlink Integration](./pattern-chainlink-integration.md)
- [Oracle Staleness Risk](./risk-oracle-staleness.md)
- [Synthetic Freshness Timestamp](../../ANTIPATTERNS.md#synthetic-freshness-timestamp)

## References

- See Source Evidence.
