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

## Trade-offs

**Pros:**
- One ERC1155 collateral interface for the bank while protocol-specific custody and reward-claim logic stays isolated in wrappers.
- Reward-index snapshots encoded in the id make claim value deterministic from the token id alone, without per-user reward state in the bank.
- Balance-delta minting tolerates fee-on-transfer and nonstandard ERC20 inputs at the wrapper boundary.
- New position types are added by deploying and whitelisting a wrapper, not by changing core bank accounting.

**Cons:**
- Id bit-packing is a correctness hazard: bounded widths, encode/decode round trips, and overflow on pool id or reward index all need explicit tests.
- Each reward-index snapshot creates a distinct id, fragmenting positions into non-fungible balances that complicate liquidation, withdrawal, and indexing.
- The oracle must trust each whitelisted wrapper's `getUnderlyingToken`/`getUnderlyingRate`; a buggy or malicious wrapper mints overvalued collateral.
- Wrapper custody concentrates the underlying LP/strategy positions in one contract, adding a custody single point of failure per integration.
- ERC1155 collateral breaks composability with ERC20-only tooling and markets, forcing bespoke integration on every consumer.

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

- Alpha Homora V2 wraps ERC20 deposits into ERC1155 ids keyed by token address with balance-delta minting in [`contracts/wrapper/WERC20.sol`](https://github.com/AlphaFinanceLab/alpha-homora-v2-contract/blob/f74fc460bd614ad15bbef57c88f6b470e5efd1fd/contracts/wrapper/WERC20.sol).
- Alpha Homora V2 encodes MasterChef and LiquidityGauge pool ids plus reward-per-share snapshots into ERC1155 ids in [`contracts/wrapper/WMasterChef.sol`](https://github.com/AlphaFinanceLab/alpha-homora-v2-contract/blob/f74fc460bd614ad15bbef57c88f6b470e5efd1fd/contracts/wrapper/WMasterChef.sol) and `WLiquidityGauge.sol`.
- Alpha Homora V2's `ProxyOracle` whitelists ERC1155 wrappers, resolves underlying token and rate from the wrapper id, then applies underlying token factors for collateral value.

## Related Patterns

- [Yield-Preserving Collateral Wrapper](./pattern-yield-preserving-collateral-wrapper.md)
- [Action-Scoped Bounded Risk Prices](../oracles/pattern-action-scoped-bounded-lending-prices.md)
- [Balance Delta Transfer Accounting](../token-integration/pattern-balance-delta-transfer-accounting.md)
