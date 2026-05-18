# Yield-Preserving Collateral Wrapper

> Wrap yield-bearing strategy shares into a non-transferable collateral token that mirrors rewards while the position is pledged in a lending market.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, collateral, wrapper, rewards, liquidation |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Users want to borrow against yield-bearing vault or strategy shares
- The base position earns rewards that should remain claimable while pledged
- A lending market requires a transfer-compatible collateral token
- Liquidation must resynchronize wrapper and underlying reward accounting

## Avoid When

- Collateral tokens must be freely transferable outside the lending market
- Rewards cannot be checkpointed before balance changes
- Liquidation cannot unwrap or resync seized collateral
- The lending market can accept the underlying strategy token directly with equivalent safety

## How It Works

The wrapper accepts strategy shares, mints non-transferable collateral, and restricts transfers to the configured lending market:

```solidity
function deposit(uint256 shares, address onBehalfOf) external {
    _checkpointRewards(onBehalfOf);
    strategy.transferFrom(msg.sender, address(this), shares);
    _mint(onBehalfOf, shares);
}

function _beforeTokenTransfer(address from, address to, uint256 amount) internal {
    require(msg.sender == lendingMarket || from == address(0) || to == address(0), "restricted");
    _checkpointRewards(from);
    _checkpointRewards(to);
}
```

Liquidation needs a dedicated path that unwraps seized collateral, stops victim reward accrual, and lets the liquidator or market receive the underlying position.

## Key Points

- Restrict transfers to the lending market and mint/burn flows.
- Block direct lending-market deposits that bypass wrapper reward accounting.
- Checkpoint reward indexes before wrapper balance changes and liquidation resync.
- Define whether liquidators receive underlying shares, wrapper tokens, or claimable rewards.
- Keep reward-claim failure from blocking liquidation liveness where possible.
- Treat wrapper exchange-rate valuation as collateral oracle risk, not guaranteed market value.

## Source Evidence

- Stake DAO's strategy wrapper creates non-transferable collateral for strategy shares, restricts transfers to the lending protocol, blocks direct deposits, and includes liquidation resync tests including reward-transfer failure cases.

## Related Patterns

- [Lazy Reward Index](../rewards/pattern-lazy-reward-index.md)
- [Exchange-Rate Valuation Risk](../oracles/risk-exchange-rate-valuation.md)
- [Comptroller Risk Gate](./pattern-comptroller-risk-gate.md)
