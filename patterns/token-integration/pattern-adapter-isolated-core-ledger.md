# Adapter-Isolated Core Ledger

> Keep the core accounting ledger free of token calls and route every token-specific behavior through small audited adapters.

## Metadata

| Property | Value |
|----------|-------|
| Category | token-integration |
| Tags | token, adapter, accounting, ledger, isolation |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- A protocol accepts multiple collateral or asset types
- Token transfer semantics, decimals, or wrappers differ across assets
- Core accounting should remain verifiable and external-call-free
- Governance can approve one adapter per supported asset behavior

## Avoid When

- The protocol only ever supports one well-understood token
- Adapters can mutate core state outside a narrow ledger interface
- Asset onboarding cannot review adapter behavior

## How It Works

The core ledger stores normalized internal balances and exposes only accounting primitives:

```solidity
function slip(bytes32 ilk, address user, int256 delta) external auth {
    collateral[ilk][user] = addSigned(collateral[ilk][user], delta);
}
```

Adapters own external token interaction:

```solidity
function join(address user, uint256 amount) external {
    token.transferFrom(msg.sender, address(this), amount);
    vat.slip(ilk, user, int256(amount * scale));
}
```

Each adapter can handle a specific token shape: exact-transfer ERC20s, rebasing wrappers, native assets, fee-on-transfer rejection, or custody receipts.

## Key Points

- Keep the core ledger free of token transfers, callbacks, approvals, and decimal reads.
- Make adapters small, asset-specific, and independently replaceable.
- Normalize units at the adapter boundary.
- Restrict adapter authorization because adapters can credit or debit core balances.
- Test that unsupported token behavior cannot leak into core accounting assumptions.

## Source Evidence

- Sky/Maker DSS keeps core collateral and debt accounting in `Vat`, while `join` adapters are the only contracts that touch external collateral token behavior.

## Related Patterns

- [Balance Delta Transfer Accounting](./pattern-balance-delta-transfer-accounting.md)
- [Missing Abstraction](../../ANTIPATTERNS.md#missing-abstraction)
- [Fee-on-Transfer Blindness](../../ANTIPATTERNS.md#fee-on-transfer-blindness)
