# Callback-Funded Lending Settlement

> Let a lending action call a borrower, supplier, or liquidator callback, then atomically pull or verify the owed assets before the action completes.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | lending, callback, flash-loan, settlement, reentrancy |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Lending actions need composable funding from another protocol in the same transaction
- The protocol can compute owed assets before the callback executes
- Token transfer behavior is curated or exact-transfer assumptions are enforced
- Reentrancy tests or formal checks cover callback-to-storage-to-callback paths

## Avoid When

- Fee-on-transfer, rebasing, or reentrant tokens are allowed
- The callback can mutate market state before the owed asset obligation is fixed
- The protocol cannot keep accounting fresh before the callback-funded action
- A normal pull-based repay, supply, or liquidation flow is sufficient

## Trade-offs

**Pros:**
- Enables leverage, refinancing, liquidation, and flash liquidity without a separate adapter
- Keeps repayment atomic with the state transition
- Lets users source funds from arbitrary integrations while the lending core keeps one settlement rule

**Cons:**
- Callback surface becomes part of the lending core's attack surface
- Exact-transfer assumptions must be explicit
- Reentrancy and stale-accounting proofs become harder

## How It Works

The lending core computes shares, debt, collateral, or liquidation proceeds first. If callback data is present, it calls the user-supplied callback, then pulls or verifies the required assets:

```solidity
function repay(uint256 assets, bytes calldata data) external {
    _accrueInterest();
    uint256 shares = _previewRepay(assets);
    _reduceBorrowShares(msg.sender, shares);

    if (data.length != 0) {
        IRepayCallback(msg.sender).onRepay(assets, data);
    }

    asset.safeTransferFrom(msg.sender, address(this), assets);
}
```

For flash loans, the core transfers assets, calls the callback, then requires the balance to have recovered before returning.

## Implementation

### Key Points
- Accrue interest before every callback-funded state transition.
- Fix the owed amount before the callback.
- Use exact-transfer or post-balance checks depending on token support policy.
- Keep callback data optional so non-composable users can use direct flows.
- Reject storage-call-storage reentrancy or prove it cannot violate market independence.
- Document unsupported token classes in the market-creation or collateral-onboarding rules.

## Source Evidence

- Morpho Blue supports callback-funded supply, collateral supply, repay, liquidation, and flash loans in `/private/tmp/defillama-source/morpho-org__morpho-blue/src/Morpho.sol`, with callback integration tests and Certora reentrancy specifications.

## Real-World Examples

- Morpho Blue callbacks let users source assets during supply, repay, liquidation, and flash-loan flows while the core still pulls or verifies repayment atomically.

## Related Patterns

- [Lending Accounting Freshness Requirements](./req-lending-accounting-freshness.md)
- [Share-Denominated Lending Accounting](./pattern-share-denominated-lending-accounting.md)
- [Verified Callback Settlement](../liquidity/pattern-verified-callback-settlement.md)
- [Fee-on-Transfer Blindness](../../ANTIPATTERNS.md#fee-on-transfer-blindness)
- [Hook/Callback Trust](../../ANTIPATTERNS.md#hookcallback-trust)
