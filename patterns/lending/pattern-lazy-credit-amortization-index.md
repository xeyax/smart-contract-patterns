# Lazy Credit Amortization Index

> Convert harvested yield into a global credit index that lazily amortizes each account's signed debt when the account interacts.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, debt, credit, yield, lazy-index |
| Complexity | High |
| Gas Efficiency | High |
| Audit Risk | High |

## Use When

- Borrower debt should be repaid by strategy yield over time
- Yield is harvested intermittently but debt reduction should be fairly distributed
- Accounts can hold signed debt balances that are updated lazily
- The protocol can define global debt weight and per-account cursor accounting

## Avoid When

- Debt must be continuously reduced in real time for all accounts
- Yield source losses can exceed modeled credit without explicit loss accounting
- Account interactions cannot afford to settle pending credit
- Credit distribution should prioritize some accounts rather than pro rata debt weight

## Trade-offs

**Pros:**
- Avoids iterating all borrowers on each harvest
- Keeps credit distribution proportional to debt weight
- Lets previews account for pending credit without global settlement

**Cons:**
- Requires signed debt and credit cursor math
- Rounding errors can accumulate if invariants are weak
- Losses need a separate accounting path

## How It Works

Harvested yield is added to a pending credit bucket and released into a global
weight accumulator. Each account stores the last accumulator value it settled:

```solidity
function harvest(uint256 yieldAmount) external {
    pendingCredit += yieldAmount;
}

function poke(address account) public {
    uint256 delta = accruedWeight - accountWeightCursor[account];
    uint256 credit = debtWeight[account] * delta / WAD;
    accountDebt[account] -= min(accountDebt[account], credit);
    accountWeightCursor[account] = accruedWeight;
}

function distributeCredit(uint256 amount) external {
    accruedWeight += amount * WAD / totalDebtWeight;
}
```

## Implementation

### Key Points

- Settle an account before minting, burning, repaying, liquidating, or transferring debt.
- Define how harvested yield unlocks into the credit index.
- Cap credit application at outstanding debt and handle fully repaid accounts.
- Track total debt weight changes after settling affected accounts.
- Test harvest timing, partial credit, full repayment, liquidation after credit, and rounding invariants.

## Source Evidence

- Alchemix V2 harvest accounting, pending credit, and account debt reduction are implemented in [`src/AlchemistV2.sol`](https://github.com/alchemix-finance/v2-foundry/blob/8915ef7b1714c16f9e260a4ef41c5f254d5b7f58/src/AlchemistV2.sol).
- Alchemix invariants around debt, credit, and collateral live in [`src/test/utils/Invariants.sol`](https://github.com/alchemix-finance/v2-foundry/blob/8915ef7b1714c16f9e260a4ef41c5f254d5b7f58/src/test/utils/Invariants.sol).

## Real-World Examples

- Alchemix V2 - harvested yield amortizes synthetic debt through lazy credit accounting.

## Related Patterns

- [Lazy Borrow Index](./pattern-lazy-borrow-index.md)
- [Share-Denominated Lending Accounting](./pattern-share-denominated-lending-accounting.md)
- [Credit Loss Accounting Requirements](./req-credit-loss-accounting.md)

## References

- See Source Evidence.
