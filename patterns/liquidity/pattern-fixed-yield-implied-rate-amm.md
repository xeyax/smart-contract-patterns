# Fixed-Yield Implied-Rate AMM

> Price fixed-maturity yield claims with implied-rate math instead of a constant-product reserve curve.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, yield, fixed-maturity, implied-rate, principal-token |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- The traded asset is a principal token, yield token, or fixed-maturity claim
- Price should converge toward known maturity behavior
- Liquidity providers need an AMM tuned for interest-rate exposure rather than spot inventory
- The protocol can maintain maturity-aware oracle and invariant math

## Avoid When

- The assets are ordinary spot tokens without maturity semantics
- Integrators expect constant-product or concentrated-liquidity behavior
- Expiry, scalar, and rate-anchor parameters cannot be calibrated or bounded
- There is not enough testing for near-expiry and extreme-proportion cases

## Trade-offs

**Pros:**
- Models yield-token economics directly
- Keeps pricing responsive to time remaining until maturity
- Can reserve fees and bound extreme PT proportions

**Cons:**
- Harder for integrators to reason about than ordinary AMMs
- Requires precise fixed-point exponent/log math
- Near-expiry behavior and oracle composition are audit-critical

## How It Works

The AMM stores reserves for standardized yield and principal tokens, then computes trades through an implied-rate curve:

```solidity
function swapSyForPt(uint256 syIn) external returns (uint256 ptOut) {
    MarketState memory state = _loadMarket();
    uint256 timeToExpiry = expiry - block.timestamp;
    uint256 impliedRate = _rateFromProportion(state, timeToExpiry);
    ptOut = _solveTrade(state, syIn, impliedRate);
    _applyFeeToReserve(syIn);
    _storeMarket(state);
}
```

The curve typically uses:

- a rate anchor from prior trades
- an expiry-sensitive scalar
- a logit-style reserve proportion
- fee and reserve accounting
- maximum PT proportion and minimum initial liquidity bounds

## Implementation

### Key Points
- Store and update implied-rate state separately from raw reserves.
- Guard maximum principal-token reserve proportion.
- Require minimum initial liquidity so early trades cannot set pathological rates.
- Handle post-expiry behavior explicitly; the curve is not meaningful after maturity.
- Use maturity-aware TWAPs instead of treating spot PT/SY reserves as ordinary token prices.
- Test extreme rates, near-expiry trades, fee reserve accounting, and rounding.

## Source Evidence

- Pendle V2 prices PT/SY markets through implied-rate math, expiry-sensitive scalar/root functions, fee-to-reserve accounting, max PT proportion, and minimum initial liquidity in `/private/tmp/defillama-source/pendle-finance__pendle-core-v2-public/contracts/core/Market/PendleMarketV7.sol` and `MarketMathCore.sol`.

## Real-World Examples

- Pendle V2 uses fixed-yield AMM math for principal-token and standardized-yield markets.

## Related Patterns

- [Fixed-Maturity Principal/Yield Tokenization](../tokens/pattern-fixed-maturity-principal-yield-tokenization.md)
- [TWAP Oracle](../oracles/pattern-twap-oracle.md)
- [Exchange-Rate Valuation Risk](../oracles/risk-exchange-rate-valuation.md)
- [Concentrated Liquidity Ranges](./pattern-concentrated-liquidity-ranges.md)
