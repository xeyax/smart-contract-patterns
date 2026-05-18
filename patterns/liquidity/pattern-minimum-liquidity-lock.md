# Minimum Liquidity Lock

> Permanently lock a small amount of initial LP supply so the first depositor cannot fully control or reset pool share price.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | amm, lp-token, initialization, dead-shares, share-price |
| Complexity | Low |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- AMM LP supply starts at zero
- Initial LP shares are minted from deposited reserves or invariant value
- A fully drained pool could be reinitialized or price-controlled by one actor
- A tiny permanent dilution is acceptable

## Avoid When

- The protocol uses virtual shares/assets or another explicit first-depositor defense
- LP supply can be safely reset only through governance migration
- Permanent locked supply would break accounting or legal requirements

## Trade-offs

**Pros:**
- Simple defense against first-LP share-price control
- Keeps `totalSupply` nonzero after ordinary withdrawals
- Makes complete pool drain harder to use as a reinitialization vector

**Cons:**
- Permanently dilutes LPs by the locked amount
- Lock size must account for token decimals and dust behavior
- Does not replace oracle, slippage, or initialization controls

## How It Works

At first deposit, mint LP shares from invariant value, send most to the depositor, and lock a minimum amount permanently:

```solidity
uint256 initialLiquidity = sqrt(amount0 * amount1);
require(initialLiquidity > MINIMUM_LIQUIDITY, "too small");

_mint(address(0), MINIMUM_LIQUIDITY);
_mint(depositor, initialLiquidity - MINIMUM_LIQUIDITY);
```

Later withdrawals reject burning the entire live supply unless the protocol has an explicit shutdown path.

## Key Points

- Require first deposit to exceed the lock amount by a meaningful margin.
- Size the lock relative to LP token decimals.
- Prevent ordinary withdrawals from draining all LP supply.
- Pair with slippage and pool-initialization controls.
- Document that locked liquidity is an accounting guard, not economic insurance.

## Source Evidence

- Raydium AMM computes initial LP shares from `sqrt(x*y)`, subtracts a decimal-scaled minimum amount from the first depositor, and rejects withdrawals that would drain all LP supply.

## Related Patterns

- [Zero Liquidity Price Control](./risk-zero-liquidity-price-control.md)
- [Virtual Share Offset](../vaults/pattern-virtual-share-offset.md)
- [LP Virtual Price Monotonicity Requirements](./req-lp-virtual-price-monotonicity.md)
