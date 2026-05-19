# Reward-Indexed ERC1155 Collateral Wrapper

> Wrap ERC20 deposits or reward-bearing pool positions into ERC1155 ids that encode the underlying asset, pool, and reward-index snapshot used for collateral valuation.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, collateral, erc1155, wrapper, rewards |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A lending protocol accepts many ERC20 or LP positions as collateral
- Some collateral positions include reward-index snapshots that affect claim value
- The bank wants one collateral interface while wrappers keep protocol-specific custody logic isolated
- The oracle can map each ERC1155 id back to an underlying asset and conversion rate

## Avoid When

- Wrapped ids cannot be decoded deterministically into the underlying position
- Reward accrual is user-specific and cannot be represented by an id-level snapshot
- The wrapper cannot custody or unwind the underlying position without external trust
- The oracle cannot validate the wrapper and underlying asset before valuing collateral

## How It Works

The simplest wrapper mints ERC1155 ids keyed by the underlying token address and
uses balance-delta accounting for deposits:

```solidity
function wrap(address token, uint256 amount) external {
    uint256 beforeBalance = IERC20(token).balanceOf(address(this));
    IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
    uint256 received = IERC20(token).balanceOf(address(this)) - beforeBalance;
    _mint(msg.sender, uint256(uint160(token)), received, "");
}
```

Pool wrappers encode pool identifiers plus a reward-index snapshot into the
ERC1155 id:

```solidity
function encodeId(uint256 poolId, uint256 rewardPerShare) internal pure returns (uint256) {
    require(poolId < 1 << 16, "pool id");
    require(rewardPerShare < 1 << 240, "reward index");
    return (poolId << 240) | rewardPerShare;
}
```

The lending oracle whitelists wrapper contracts, decodes each id to its
underlying token and conversion rate, then applies action-scoped collateral
factors to the underlying value:

```solidity
function collateralValue(address wrapper, uint256 id, uint256 amount) external view returns (uint256) {
    require(whitelistedWrapper[wrapper], "wrapper");
    address underlying = IERC20Wrapper(wrapper).getUnderlyingToken(id);
    uint256 rate = IERC20Wrapper(wrapper).getUnderlyingRate(id);
    return _discountedUnderlyingValue(underlying, amount * rate / Q112);
}
```

## Key Points

- Encode every economically relevant position dimension into the ERC1155 id.
- Use balance-delta minting for fee-on-transfer or nonstandard ERC20 inputs, or reject those tokens at onboarding.
- Keep wrapper custody and reward-claim mechanics outside the bank's core accounting.
- Whitelist wrapper contracts and validate the decoded underlying asset before collateral valuation.
- Bound id bit widths and test decode/encode round trips.
- Document whether reward-index differences make two ids non-fungible for liquidation or withdrawal.

## Source Evidence

- Alpha Homora V2 wraps ERC20 deposits into ERC1155 ids keyed by token address with balance-delta minting in `/private/tmp/defillama-source/AlphaFinanceLab__alpha-homora-v2-contract/contracts/wrapper/WERC20.sol`.
- Alpha Homora V2 encodes MasterChef and LiquidityGauge pool ids plus reward-per-share snapshots into ERC1155 ids in `/private/tmp/defillama-source/AlphaFinanceLab__alpha-homora-v2-contract/contracts/wrapper/WMasterChef.sol` and `WLiquidityGauge.sol`.
- Alpha Homora V2's `ProxyOracle` whitelists ERC1155 wrappers, resolves underlying token and rate from the wrapper id, then applies underlying token factors for collateral value.

## Related Patterns

- [Yield-Preserving Collateral Wrapper](./pattern-yield-preserving-collateral-wrapper.md)
- [Action-Scoped Bounded Risk Prices](../oracles/pattern-action-scoped-bounded-lending-prices.md)
- [Balance Delta Transfer Accounting](../token-integration/pattern-balance-delta-transfer-accounting.md)
