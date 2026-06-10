# Consumable Borrow-Right Credit Meter

> Represent borrow capacity as a transferable token that is continuously consumed by outstanding debt over time.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, borrow-right, credit, fixed-rate, debt-meter |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Borrowing should have a separate prepaid or market-priced right instead of an interest rate charged on principal
- Debt consumes that right continuously while it is outstanding
- Borrow rights may be minted, sold, delegated, or replenished independently from collateral
- The market can define what happens when a borrower runs a right-token deficit

## Avoid When

- Debt interest should accrue directly to lenders or reserves
- Borrow rights cannot be liquidated, replenished, or priced safely during stress
- Transfers of borrow rights would create unacceptable secondary-market or compliance risk
- Borrowers must never enter a negative-right state

## Trade-offs

**Pros:**
- Separates debt principal from the cost of maintaining debt over time
- Lets borrow rights trade or be distributed independently of collateral
- Gives liquidators or keepers an explicit deficit to resolve

**Cons:**
- Adds a second solvency dimension besides collateral value
- Deficit replenishment can increase debt and must be bounded
- Balance views are time-dependent and easy for integrators to misread

## How It Works

Each borrower has outstanding debt and a borrow-right balance. The effective right balance subtracts elapsed debt-time:

```solidity
function balanceOf(address user) public view returns (uint256) {
    uint256 accrued = (block.timestamp - lastUpdated[user]) * debt[user] / YEAR;
    uint256 consumed = due[user] + accrued;
    return consumed >= rawBalance[user] ? 0 : rawBalance[user] - consumed;
}
```

Borrowing increases debt and starts consuming rights. Repayment decreases debt and stops future consumption. If consumption exceeds the borrow-right balance, the account has a deficit:

```solidity
function deficitOf(address user) public view returns (uint256) {
    uint256 accrued = (block.timestamp - lastUpdated[user]) * debt[user] / YEAR;
    uint256 consumed = due[user] + accrued;
    return consumed > rawBalance[user] ? consumed - rawBalance[user] : 0;
}
```

A deficit can block collateral withdrawals, trigger forced replenishment, or become part of liquidation eligibility. If the protocol allows forced replenishment, replenishment should mint or credit rights while adding a bounded debt cost and paying an explicit keeper incentive.

## Key Points

- Settle or checkpoint right consumption before borrow, repay, transfer, withdrawal, replenishment, and liquidation.
- Distinguish raw token supply from effective circulating supply after accrued consumption.
- Bound replenishment price, incentive, and added debt so deficit resolution cannot bankrupt otherwise healthy collateral.
- Block collateral withdrawals while the account has a borrow-right deficit.
- Document whether borrow rights are transferable, permit-enabled, mintable by governance, or market-specific.
- Test long idle periods, partial repayment, transfer after consumption, forced replenishment, and liquidation with a right-token deficit.

## Source Evidence

- Inverse FiRM implements DOLA Borrow Rights as a transferable ERC20-like meter whose `balanceOf`, `deficitOf`, and `signedBalanceOf` subtract elapsed debt-time in [`src/DBR.sol`](https://github.com/InverseFinance/FiRM/blob/6cd9f06cd0da79ccaad9f663aed299ef3021af10/src/DBR.sol).
- Inverse FiRM markets increase the DBR debt meter on borrow, reduce it on repay, block withdrawals with a DBR deficit, and allow forced replenishment that adds DOLA debt in [`src/Market.sol`](https://github.com/InverseFinance/FiRM/blob/6cd9f06cd0da79ccaad9f663aed299ef3021af10/src/Market.sol).

## Real-World Examples

- Inverse FiRM - DBR tokens represent the right to maintain DOLA debt over time.

## Related Patterns

- [Lazy Credit Amortization Index](./pattern-lazy-credit-amortization-index.md)
- [Nontransferable Debt Token Delegation](./pattern-nontransferable-debt-token-delegation.md)
- [Credit Loss Accounting Requirements](./req-credit-loss-accounting.md)
