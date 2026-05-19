# Liability-Backed ERC4626 Savings Share

> Use ERC4626 shares to represent protocol liabilities where deposits burn the base asset and withdrawals mint it back from controlled supply.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | erc4626, savings, stablecoin, liability, index |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | High |

## Use When

- A stablecoin or credit protocol wants an ERC4626-compatible savings token
- The share asset is a protocol liability rather than externally custodied vault inventory
- Deposits should reduce circulating base-asset supply and withdrawals should recreate it
- A compounding index defines how many base assets each share can claim
- Minting and burning the base asset are already bounded by a solvency or supply-control module

## Avoid When

- The vault actually custodies third-party assets and `totalAssets()` should reflect token balances
- The protocol cannot safely mint the base asset on withdrawal
- Savings liabilities can grow without a cap, rate bound, or balance-sheet check
- Integrators are likely to assume `asset().balanceOf(vault)` backs the shares

## Trade-offs

**Pros:**
- Keeps the user and integrator interface close to ERC4626
- Avoids idle asset custody inside the savings token
- Makes yield accrual a deterministic index calculation

**Cons:**
- Requires strong supply-mutation controls outside the vault
- `totalAssets()` is a liability view, not a custody proof
- Rate updates, rounding, and caps become solvency-sensitive

## How It Works

The vault stores a compounding factor. Deposits burn the base asset from the
caller and mint savings shares. Withdrawals burn shares and mint the base asset
to the receiver:

```solidity
function totalAssets() public view returns (uint256) {
    return convertToAssets(totalSupply(), Rounding.Up);
}

function _deposit(address caller, address receiver, uint256 assets, uint256 shares) internal {
    require(totalAssetsAfter(shares) <= notionalCap, "cap");
    stablecoin.burnFrom(caller, assets);
    _mint(receiver, shares);
}

function _withdraw(address caller, address receiver, address owner, uint256 assets, uint256 shares) internal {
    _spendAllowanceIfNeeded(caller, owner, shares);
    _burn(owner, shares);
    stablecoin.mint(receiver, assets);
}
```

Rate changes first crystallize the old index, then store the new rate and
timestamp so preview and execution paths share the same accrued basis.

## Key Points

- Document that `totalAssets()` reports owed stablecoin, not token custody.
- Gate base-asset mint and burn authority through a balance-sheet, cap, or controller module.
- Bound rates and update the accumulated index before changing the rate.
- Apply conservative rounding to caps and liabilities.
- Keep preview and execution conversions on the same index basis.
- Test cap enforcement, deposit/withdraw round trips, fuzzed conversion monotonicity, and that unrelated base-asset balances cannot change share value.

## Source Evidence

- Reservoir's sRUSD v2 `Savingcoin` extends ERC4626, burns rUSD on deposit, mints rUSD on withdrawal, derives `totalAssets()` from share supply and a compounding factor, and enforces a notional cap in `/private/tmp/defillama-source/reservoir-protocol__srusd/src/Savingcoin.sol`.
- Reservoir sRUSD tests cover cap behavior, conversion checks, fuzzed deposit/withdraw flows, and no-stuck-rUSD invariants in `/private/tmp/defillama-source/reservoir-protocol__srusd/test`.

## Related Patterns

- [Delta NAV Share Accounting](./pattern-delta-nav.md)
- [Bounded Continuous Compounding Index](../math/pattern-bounded-continuous-compounding-index.md)
- [Balance-Sheet Solvency Gate](../lending/pattern-balance-sheet-solvency-gate.md)
- [Privileged Supply Mutation](../../ANTIPATTERNS.md#privileged-supply-mutation)
