# Nontransferable Debt Token Delegation

> Represent borrow liabilities as non-transferable debt tokens and expose delegated borrowing through a separate allowance surface.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, debt-token, delegation, allowance, liability |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Borrow balances are represented as tokenized liabilities
- Debt should not be sold or transferred like an asset claim
- Users need to authorize another account to borrow on their behalf
- Delegated borrowing can run through normal collateral and risk checks

## Avoid When

- Debt transfers are a deliberate market feature with separate risk controls
- Delegation cannot be bounded by amount, rate mode, asset, or expiry
- Borrow allowance is implemented with normal ERC20 allowance semantics
- Liquidation or health checks cannot attribute debt to the delegator

## Trade-offs

**Pros:**
- Prevents liability transfer from bypassing account health checks
- Keeps debt accounting compatible with tokenized balance views
- Gives credit delegation a narrow, auditable approval surface

**Cons:**
- Delegation adds another allowance ledger and UX surface
- Users may expect ERC20-like transfers from token interfaces
- Revocation and partial allowance consumption need careful tests

## How It Works

Debt tokens expose balance views but revert ERC20 transfer and approve paths. A
separate borrow-allowance ledger authorizes a delegate to create debt for a user,
and the lending pool consumes that allowance only after normal borrow validation.

```solidity
function transfer(address, uint256) external pure returns (bool) {
    revert("debt non-transferable");
}

function approveDelegation(address delegatee, uint256 amount) external {
    borrowAllowance[msg.sender][delegatee] = amount;
}

function borrowOnBehalf(address user, uint256 amount) external {
    _consumeBorrowAllowance(user, msg.sender, amount);
    _validateBorrow(user, amount);
    _mintDebt(user, amount);
}
```

## Implementation

- Revert transfer, transferFrom, approve, increaseAllowance, and decreaseAllowance on debt tokens.
- Keep borrow delegation in a separate allowance ledger.
- Consume delegation before or atomically with debt creation so reentrancy cannot reuse it.
- Bind delegation to the borrower, delegatee, asset, rate mode, and optional expiry when relevant.
- Test ordinary borrow, delegated borrow, allowance exhaustion, revocation, and flash-loan debt conversion.

## Source Evidence

- Aave V2 debt tokens revert ERC20 transfer and allowance paths while using separate borrow allowance consumption in `/private/tmp/defillama-source/aave__protocol-v2/contracts/protocol/tokenization/base/DebtTokenBase.sol`.
- Aave V2 flash-loan tests cover delegated stable-debt allowance requirements in `/private/tmp/defillama-source/aave__protocol-v2/test-suites/test-aave/flashloan.spec.ts`.

## Real-World Examples

- Aave V2 uses non-transferable debt tokens with separate credit-delegation allowances.

## Related Patterns

- [Debt-Converting Flash Loan](./pattern-debt-converting-flash-loan.md)
- [Comptroller Risk Gate](./pattern-comptroller-risk-gate.md)
- [Signature Scope Drift](../../ANTIPATTERNS.md#signature-scope-drift)

## References

- Aave V2 debt token source.
