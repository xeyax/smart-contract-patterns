# Collateralized Option Liquidity Pool

> Split option-pool liquidity into free and reserved collateral while minting long/short option claims from the same ERC1155-style ledger.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | options, liquidity, collateral, erc1155, utilization |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Liquidity providers underwrite options from shared collateral
- Long and short option claims need standardized token ids by maturity, strike, and side
- Option purchases should reserve collateral and update pool utilization
- Pricing depends on volatility, utilization, and slippage coefficients

## Avoid When

- Options are fully order-book based with no pooled underwriter collateral
- Collateral can be rehypothecated without per-option reservation
- The pricing surface or oracle cannot be trusted for max-cost purchases
- ERC1155 token ids would be hard for integrators to decode safely

## Trade-offs

**Pros:**
- Separates free liquidity from collateral reserved for written options
- Lets option claims and liquidity claims share one compact token ledger
- Allows utilization-aware pricing and mining rewards

**Cons:**
- Token-id semantics are complex and must be documented precisely
- Collateral reservation loops can become expensive without bounds
- Volatility and spot inputs become critical economic dependencies

## How It Works

Define token ids for free liquidity, reserved liquidity, long calls, short calls, long puts, and short puts. When a buyer purchases an option, quote the premium from spot, strike, maturity, implied volatility, and current utilization:

```solidity
function purchase(Option memory o, uint256 size, uint256 maxCost) external {
    Quote memory q = _quote(o, size);
    require(q.cost + q.fee <= maxCost, "cost");

    _mint(msg.sender, longTokenId(o), size);
    _reserveUnderwriterCollateral(o, size, q.cost);
    _updateUtilization(o.side);
}
```

The pool burns free-liquidity claims from underwriters, mints reserved-liquidity or short-option claims, and records the minimum collateralization level for the long token id.

## Key Points

- Make token-id encoding unambiguous for side, maturity, strike, and claim type.
- Reserve collateral before or atomically with minting long option claims.
- Require user max-cost bounds for purchases and refund any swap surplus.
- Update utilization and reward indexes before changing free or reserved liquidity.
- Test deep in-the-money, out-of-the-money, near-expiry, no-liquidity, and max-cost branches.

## Source Evidence

- Premia stores option-pool token types, free/reserved liquidity, long/short calls and puts, pricing state, and user TVL in `/private/tmp/defillama-source/premiafinance__premia-contracts/contracts/pool/PoolStorage.sol`.
- Premia quotes option purchases from volatility, utilization, and pool liquidity and mints long claims while reserving underwriter liquidity in `/private/tmp/defillama-source/premiafinance__premia-contracts/contracts/pool/PoolInternal.sol`.
- Premia purchase entrypoints enforce max-cost bounds and refund swap surplus in `/private/tmp/defillama-source/premiafinance__premia-contracts/contracts/pool/PoolWrite.sol`.

## Real-World Examples

- Premia - ERC1155 option pools with free and reserved liquidity claims.

## Related Patterns

- [Lazy Reward Index](../rewards/pattern-lazy-reward-index.md)
- [Missing Slippage Protection](../../ANTIPATTERNS.md#missing-slippage-protection)
- [Action-Scoped Bounded Risk Prices](../oracles/pattern-action-scoped-bounded-lending-prices.md)
