# Manager-Owned Derivative Cash Settlement

> Let asset contracts compute derivative settlement while a risk manager owns the authoritative cash adjustment and settled-cash record.

## Metadata

| Property | Value |
|----------|-------|
| Category | perps |
| Tags | perps, options, settlement, cash, manager |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Derivative assets need settlement, expiry, funding, or exercise logic
- Account solvency depends on a manager-controlled cash ledger
- Assets can compute settlement amounts but should not freely mutate cash balances
- Settlement must update risk state and cash accounting atomically

## Avoid When

- Assets can safely own their own isolated collateral and cash ledgers
- The manager cannot validate the account after settlement
- Asset settlement hooks can be called by arbitrary accounts without context
- Cash adjustments are not replay-protected by trade id, expiry, or settled state

## Trade-offs

**Pros:**
- Keeps cash authority in the same component that owns risk checks
- Lets derivative assets stay focused on payoff calculation
- Reduces cross-asset settlement drift

**Cons:**
- The manager becomes a critical settlement authority
- Asset-manager interfaces are tightly coupled
- Settlement replay and stale-risk updates are high-severity bugs

## How It Works

The asset computes settlement or funding deltas, but the manager applies cash
balance changes and records settled cash or trade ids under its own authority.

```solidity
function settle(uint256 accountId, uint256 assetId) external {
    Settlement memory s = IAsset(assetId).computeSettlement(accountId);
    require(!settled[s.settlementId], "settled");

    _adjustCash(accountId, s.cashDelta);
    settled[s.settlementId] = true;
    _validateAccount(accountId);
}
```

The same ownership boundary applies when external synth or perps markets report
debt into a shared core. Market modules can compute debt and reported issuance,
but the manager should own USD mint/burn, net issuance, withdrawable credit, and
collateral-backed debt accounting.

## Implementation

- Bind settlement ids to account, asset, expiry, market, and trade context.
- Let only the manager or authorized settlement path mutate cash.
- Record settled cash before or atomically with external effects.
- Re-run account risk checks after settlement.
- Test duplicate settlement, partial expiry, funding accrual, negative cash, and manager pause behavior.
- For external market modules, prove market-reported debt cannot mint or burn the
  core cash asset except through manager-owned issuance paths.

## Source Evidence

- Derive V2 documents asset settlement responsibilities in `/private/tmp/defillama-source/derivexyz__v2-core/docs/assets.md`.
- Derive V2 manager settlement and cash adjustment logic appears in `src/risk-managers/BaseManager.sol`, while option and cash assets compute settlement behavior in `src/assets/OptionAsset.sol` and `src/assets/CashAsset.sol`.
- Synthetix V3 lets external markets compute and report debt while core modules
  own USD issuance, net issuance, withdrawable credit, and collateral-backed debt
  accounting in `/private/tmp/defillama-source/synthetixio__synthetix-v3/protocol/synthetix/contracts/storage/Market.sol:50-83`,
  `/private/tmp/defillama-source/synthetixio__synthetix-v3/protocol/synthetix/contracts/modules/core/MarketManagerModule.sol:254-342`,
  and `/private/tmp/defillama-source/synthetixio__synthetix-v3/protocol/synthetix/contracts/modules/core/IssueUSDModule.sol:60-118`.

## Real-World Examples

- Derive V2 computes option and perp settlement through asset contracts while manager-controlled paths adjust and record cash.

## Related Patterns

- [Hook-Validated Subaccount Ledger](../access-control/pattern-hook-validated-subaccount-ledger.md)
- [Capped PnL Impact Pool Risk Accounting](./pattern-capped-pnl-impact-pool-risk-accounting.md)
- [Hook/Callback Trust](../../ANTIPATTERNS.md#hookcallback-trust)

## References

- Derive V2 asset and manager source.
