# Collateral-Ratio Pro-Rata Redemption

> Burn a stable asset for a pro-rata claim on current reserves while using oracle value only to price the global collateral-ratio penalty.

## Metadata

| Property | Value |
|----------|-------|
| Category | token-integration |
| Tags | stablecoin, redemption, reserves, collateral-ratio, pro-rata |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A stable asset is backed by multiple collateral and managed subcollateral
  balances
- Redemptions should give every redeemer the same reserve composition at the
  current accounting state
- Oracle value should determine solvency penalties, not arbitrary token
  selection
- Some output collateral may be non-transferable, permissioned, or forfeitable

## Avoid When

- The protocol promises single-asset redemption at par
- Reserve accounting cannot enumerate managed balances safely
- Whitelisted or non-transferable collateral cannot be handled explicitly
- Oracle failures should fully block redemptions instead of applying a documented
  collateral-ratio rule

## How It Works

The redeemer burns stable assets and receives a pro-rata share of each reserve
balance. Oracle values compute the global collateral ratio and any redemption
penalty; they do not decide per-token output weights:

```solidity
function redeem(uint256 stableAmount, address[] calldata tokens, uint256[] calldata minOuts) external {
    uint256 penalty = collateralRatioPenalty();
    _burn(msg.sender, stableAmount);

    for (uint256 i; i < tokens.length; i++) {
        uint256 out = reserves[tokens[i]] * stableAmount / totalIssued;
        out = out * (BPS - penalty) / BPS;
        require(out >= minOuts[i], "min out");
        _sendOrForfeit(tokens[i], msg.sender, out);
    }
}
```

If issuance is tracked per collateral through normalizers, redemption should
shrink each collateral's issued stable amount proportionally and renormalize when
bounds are hit so aggregate issuance remains consistent.

## Key Points

- Bind the output token list and `minAmountOuts` to the redemption transaction.
- Burn or escrow stable assets in the same transaction that releases collateral.
- Compute reserve outputs from current reserve balances, including managed
  subcollateral.
- Use oracle value for the global collateral-ratio penalty only.
- Make forfeiture of non-transferable or non-whitelisted outputs explicit.
- Test proportional issuance shrinkage, normalizer bounds, forfeited outputs,
  and reserve balances with zero or dust amounts.

## Source Evidence

- Angle Transmuter redemption burns stable assets and computes pro-rata reserve
  outputs across collateral and subcollateral in `/private/tmp/defillama-source/angleprotocol__angle-transmuter/contracts/transmuter/facets/Redeemer.sol:46-148`.
- Angle applies collateral-ratio and redemption-penalty accounting without using
  oracle values to reweight every output token in `/private/tmp/defillama-source/angleprotocol__angle-transmuter/contracts/transmuter/facets/Redeemer.sol:150-223`
  and `/private/tmp/defillama-source/angleprotocol__angle-transmuter/contracts/transmuter/libraries/LibGetters.sol:23-91`.
- Angle fuzz tests cover pro-rata redemption, output-token binding, forfeiture,
  and normalizer behavior in `/private/tmp/defillama-source/angleprotocol__angle-transmuter/test/fuzz/RedeemTest.t.sol:264-517`.

## Related Patterns

- [Balance Delta Transfer Accounting](./pattern-balance-delta-transfer-accounting.md)
- [Reserve Exposure Caps](../lending/pattern-reserve-exposure-caps.md)
- [Action-Scoped Bounded Risk Prices](../oracles/pattern-action-scoped-bounded-lending-prices.md)
- [Balance-Sheet Solvency Gate](../lending/pattern-balance-sheet-solvency-gate.md)
