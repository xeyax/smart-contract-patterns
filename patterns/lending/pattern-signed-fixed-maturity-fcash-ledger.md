# Signed Fixed-Maturity fCash Ledger

> Track fixed-maturity asset and debt claims as signed balances that settle into cash after maturity.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, fixed-maturity, fcash, erc1155, settlement |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A protocol needs positive fixed-maturity claims and negative fixed-maturity debt in one ledger
- Positive claims can be transferred externally while debt remains subject to account health checks
- Matured positions settle into a cash or prime-cash balance
- Free-collateral checks can price all active maturities consistently

## Avoid When

- Debt positions must be freely transferable
- Maturity settlement cannot be priced deterministically
- Account health checks cannot include all signed balances
- A simpler per-maturity ERC20 claim is sufficient

## Trade-offs

**Pros:**
- One maturity id can represent both lender claims and borrower debt
- Positive claims are composable without making debt transferable
- Settlement into cash can be lazy and account-local

**Cons:**
- Signed balances are harder for integrators to reason about
- Transfers must reject or constrain negative balances
- Free-collateral checks become part of token transfer safety

## How It Works

Each account stores signed balances per currency and maturity. Lending increases
positive fCash; borrowing creates negative fCash and increases present cash.
After maturity, the fixed-maturity position settles into the cash ledger:

```solidity
function borrow(uint16 currency, uint40 maturity, int256 fCashDebt) external {
    require(fCashDebt < 0, "not debt");
    balances[msg.sender][currency][maturity] += fCashDebt;
    cashBalance[msg.sender][currency] += presentValue(-fCashDebt, maturity);
    require(_isCollateralized(msg.sender), "free collateral");
}

function settle(uint16 currency, uint40 maturity, address account) external {
    int256 fCash = balances[account][currency][maturity];
    delete balances[account][currency][maturity];
    cashBalance[account][currency] += fCash;
}
```

## Implementation

### Key Points

- Keep positive and negative balances in the same maturity domain but enforce different transfer rules.
- Include maturity, currency, and settlement asset in every id.
- Run account-health checks after borrowing, transferring, or settling debt-bearing accounts.
- Define the settlement conversion and rounding direction before launch.
- Test positive transfers, negative-transfer rejection, maturity settlement, partial liquidation, and free-collateral edge cases.

## Source Evidence

- Notional V3 represents fCash through ERC1155-style ids and transfer hooks in `/private/tmp/defillama-source/notional-finance__contracts-v3/contracts/external/actions/ERC1155Action.sol`.
- Notional prime-cash conversion and settlement math are in `/private/tmp/defillama-source/notional-finance__contracts-v3/contracts/internal/pCash/PrimeRateLib.sol`.
- Notional stateful lend and borrow tests cover fCash behavior under `/private/tmp/defillama-source/notional-finance__contracts-v3/tests/stateful`.

## Real-World Examples

- Notional V3 - signed fCash balances settle into prime cash after maturity.

## Related Patterns

- [Rolling Fixed-Maturity Debt Tokens](./pattern-rolling-fixed-maturity-debt-tokens.md)
- [Lazy Borrow Index](./pattern-lazy-borrow-index.md)
- [Collateral Threshold Separation Requirements](./req-collateral-threshold-separation.md)

## References

- See Source Evidence.
