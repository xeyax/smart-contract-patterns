# Hook-Validated Subaccount Ledger

> Keep multi-asset subaccount balances in a core ledger while managers and asset hooks validate every transfer batch.

## Metadata

| Property | Value |
|----------|-------|
| Category | access-control |
| Tags | access-control, subaccount, hooks, ledger, allowance |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Accounts hold many asset balances under one subaccount id
- Transfers must be validated by a manager or risk engine
- Assets need hooks for settlement, margin, or accounting side effects
- Directional allowances or permits should authorize only specific balance movement

## Avoid When

- A simple ERC20 or ERC721 ownership model is enough
- Hooks can call back into the ledger without a shared reentrancy model
- Manager checks are optional or can be skipped for some asset ids
- Allowances are too broad to bind account, asset, amount, and direction

## Trade-offs

**Pros:**
- Centralizes multi-asset accounting in one ledger
- Lets each asset or manager enforce its own risk constraints
- Supports subaccount ownership, permits, and directional allowances

**Cons:**
- Hook ordering and reentrancy are hard to audit
- Managers become critical trust and upgrade boundaries
- Batch validation must avoid both over-checking and skipped checks

## How It Works

Represent each subaccount as an owned account id with internal balances by asset.
Before or after a batch transfer, call asset hooks and the subaccount manager to
validate account state and settlement side effects.

```solidity
function transferBatch(Transfer[] calldata transfers) external {
    _consumeDirectionalAllowances(msg.sender, transfers);

    for (uint256 i; i < transfers.length; i++) {
        _applyBalanceDelta(transfers[i]);
        IAsset(transfers[i].asset).onBalanceChange(transfers[i]);
    }

    IManager(managerOf(transfers)).validateAccountState(affectedAccounts(transfers));
}
```

## Implementation

- Bind allowances or permits to subaccount id, asset, direction, amount, nonce, and expiry.
- Run manager state checks once per affected account batch.
- Keep hook interfaces narrow and document whether hooks run before or after balance writes.
- Share a reentrancy model across ledger, manager, and asset hooks.
- Test same-type asset swaps, allowance direction, permit replay, hook revert, and manager-state failure.

## Source Evidence

- Derive V2 documents ERC721 subaccounts with multi-asset balances in `/private/tmp/defillama-source/derivexyz__v2-core/docs/subaccounts.md`.
- Derive V2 implements balance transfers, asset hooks, manager checks, allowances, and permit tests in `src/SubAccounts.sol`, `src/Allowances.sol`, and account unit tests.

## Real-World Examples

- Derive V2 uses subaccounts as a hook-validated multi-asset ledger for derivative positions and cash balances.

## Related Patterns

- [Adapter-Isolated Core Ledger](../token-integration/pattern-adapter-isolated-core-ledger.md)
- [Selector-Scoped Authority](./pattern-selector-scoped-authority.md)
- [Hook/Callback Trust](../../ANTIPATTERNS.md#hookcallback-trust)

## References

- Derive V2 subaccount documentation and source.
