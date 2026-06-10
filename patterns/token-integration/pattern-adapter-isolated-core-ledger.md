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

## Trade-offs

**Pros:**
- The core ledger makes no external calls, so reentrancy and weird-token behavior cannot reach core invariants.
- Token quirks (decimals, fees, rebasing, native assets) are contained in small per-asset adapters that are individually auditable.
- New asset shapes onboard by adding an adapter without touching or re-auditing core accounting.
- Unit normalization happens once at the adapter boundary, keeping internal math uniform.

**Cons:**
- Adapters are fully trusted: an authorized adapter can credit or debit core balances, so every onboarding is a critical review.
- The extra hop per deposit/withdraw adds gas and another authorization layer to manage.
- Adapter proliferation creates operational sprawl — versioning, deprecation, and auth lists to govern per asset.
- Overkill for single-token protocols; the indirection costs more than it isolates.
- Sign or scale bugs at the adapter/ledger interface silently corrupt normalized balances.

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
