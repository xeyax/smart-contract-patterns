# Adapter-Routed Index Rebalance

> Rebalance an index token toward manager targets through approved traders and exchange adapters with cooldowns and per-trade limits.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, index, rebalance, adapter, manager, trader |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A portfolio manager sets target component units for an index token
- Trades should move positions toward targets without launching a public auction
- Execution should route through registered exchange adapters rather than arbitrary calldata
- Traders need per-component cooldowns, size limits, and slippage bounds

## Avoid When

- Rebalances require competitive price discovery or public bidder execution
- Any caller can trade without meaningful slippage and target constraints
- Exchange adapters can call arbitrary targets or mutate unrelated portfolio state
- The portfolio contains external positions that cannot be traded proportionally

## Trade-offs

**Pros:**
- Gives managers operational flexibility without direct token custody
- Lets permissioned traders execute partial rebalances over time
- Adapter boundaries make execution surfaces reviewable

**Cons:**
- Less price-discovery protection than auction-based rebalancing
- Trader and adapter configuration becomes an economic control plane
- EOA-only public trading gates can harm smart-account and router compatibility

## How It Works

The manager starts a rebalance by setting target units for old and new components:

```solidity
function startRebalance(address[] calldata components, uint256[] calldata targets) external onlyManager {
    _rejectExternalPositions(components);
    _storeTargets(components, targets, currentPositionMultiplier());
}
```

Allowed traders then call `trade` for a component. The module validates the component target, cooldown, adapter, and ETH-denominated max/min limit, computes the trade size that moves toward the target, executes through the selected adapter, accrues fees, and updates component units:

```solidity
function trade(address component, uint256 ethLimit) external onlyTrader {
    _validateTrade(component);
    Trade memory t = _createTrade(component, ethLimit);
    _executeViaAdapter(t);
    _updatePositionState(t);
}
```

## Key Points

- Store targets against the position multiplier used to compute them, and normalize if fees change the multiplier.
- Reject components with external positions unless the rebalance module knows how to unwind them safely.
- Scope trader permissions and public-trading modes separately.
- Require per-trade max spend or min receive limits to bound sandwich and adapter execution risk.
- Apply cooldowns between component trades so repeated calls cannot churn the same component instantly.
- Register adapters by integration name and review their target, selector, and calldata assumptions.

## Source Evidence

- Set Protocol V2 `GeneralIndexModule` stores manager target units, validates old/new components, rejects external positions, allows approved traders to trade toward targets, and executes through exchange adapters in `/private/tmp/defillama-source/SetProtocol__set-protocol-v2/contracts/protocol/modules/v1/GeneralIndexModule.sol`.

## Real-World Examples

- Set Protocol V2 - GeneralIndexModule rebalances SetToken components through approved traders and exchange adapters.

## Related Patterns

- [Bounded Rebalance Auction](./pattern-bounded-rebalance-auction.md)
- [Module-Owned Portfolio Position Ledger](./pattern-module-owned-portfolio-position-ledger.md)
- [Premium Buffer](./pattern-premium-buffer.md)
- [Missing Slippage Protection](../../ANTIPATTERNS.md#missing-slippage-protection)
