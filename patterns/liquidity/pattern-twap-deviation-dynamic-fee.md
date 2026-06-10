# TWAP-Deviation Dynamic Fee

> Adjust AMM swap fees by the bounded deviation between current price and a recent TWAP.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, dynamic-fee, twap, volatility, concentrated-liquidity |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- AMM fee should rise during short-term price dislocation or volatility
- A recent TWAP is available from the pool's observation history
- The fee formula can be bounded by governance-set min and max values
- The pool should fall back safely when the TWAP window is unavailable

## Avoid When

- Pool observations are too sparse or manipulable
- Users need fixed, predictable swap fees
- Dynamic fees can be keyed by unsafe caller identity such as `tx.origin`

## Trade-offs

**Pros:**
- Charges more when the current tick diverges from recent history
- Can reduce toxic flow during volatile periods
- Reuses TWAP observations already maintained by many CL AMMs

**Cons:**
- TWAP lag can overcharge during legitimate repricing
- Fee calculation becomes another oracle-like dependency
- Observation gaps need explicit fallback behavior

## How It Works

The fee module compares the current tick to a historical TWAP tick. The dynamic
component is proportional to absolute deviation and capped by configured bounds.

```solidity
function getFee(PoolKey memory key) external view returns (uint24 fee) {
    (bool ok, int24 twapTick) = _recentTwapTick(key.pool);
    if (!ok) return baseFee;

    int24 currentTick = _currentTick(key.pool);
    uint256 deviation = abs(currentTick - twapTick);
    uint256 dynamicFee = baseFee + deviation * feeFactor;
    return uint24(min(dynamicFee, maxFee));
}
```

## Implementation

- Define the observation window and fallback fee for insufficient history.
- Cap dynamic fee and validate fee-factor updates.
- Keep user discounts or fee exemptions independent of `tx.origin`.
- Test zero observations, stale observations, current-equals-TWAP, maximum deviation, and governance bounds.
- Document that this reduces adverse selection; it does not prove price accuracy.

## Source Evidence

- Aerodrome Slipstream computes dynamic fees in [`contracts/core/fees/DynamicSwapFeeModule.sol`](https://github.com/aerodrome-finance/slipstream/blob/f8717faaae6e6717db3c8e3850149c01a79c0603/contracts/core/fees/DynamicSwapFeeModule.sol) through `getFee` and `_getDynamicFee`.
- Aerodrome documents the module in `contracts/core/fees/README.md`.
- Aerodrome fork tests cover fee calculation in `test/fork/CustomFeeModule/DynamicSwapFeeModule/getFee/getFee.t.sol`.

## Real-World Examples

- Aerodrome Slipstream uses a TWAP-deviation fee module for concentrated-liquidity swaps.

## Related Patterns

- [Volatility Accumulator Dynamic Fee](./pattern-volatility-accumulator-dynamic-fee.md)
- [TWAP Oracle](../oracles/pattern-twap-oracle.md)
- [Offpeg Dynamic Fee](./pattern-offpeg-dynamic-fee.md)

## References

- Aerodrome Slipstream dynamic fee module.
