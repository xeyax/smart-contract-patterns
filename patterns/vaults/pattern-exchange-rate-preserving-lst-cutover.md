# Exchange-Rate Preserving LST Cutover

> Migrate a liquid-staking token to a successor manager by moving backing assets without minting and asserting exchange-rate continuity.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, liquid-staking, migration, exchange-rate, cutover |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A liquid-staking system must migrate manager contracts without changing token claims
- Old and new entrypoints can be paused during cutover
- Backing assets can be moved without minting successor shares
- The migration runbook can assert exchange-rate continuity before unpause

## Avoid When

- Users cannot independently verify post-migration backing
- The old manager still accepts deposits or withdrawals during cutover
- Migration custody relies only on an undocumented social process
- Exchange-rate rounding differences cannot be bounded

## Trade-offs

**Pros:**
- Token holders keep the same claims through migration; no snapshot, airdrop, or user action required.
- The on-chain rate-continuity assertion converts a social promise ("backing moved correctly") into a hard revert condition.
- Move-without-minting keeps supply fixed, so downstream integrations pricing the LST see no rate discontinuity.
- Pause-bracketed cutover eliminates mid-migration deposit/withdrawal races by construction.

**Cons:**
- Requires a full protocol pause: deposits, withdrawals, mints, and burns are frozen for the entire custody handoff, with user-facing downtime.
- The migration path itself is one-shot, high-privilege code that is hard to test against real mainnet state and is exactly where a bug is unrecoverable.
- Rounding tolerance is a judgment call: too tight bricks the migration, too loose hides backing loss.
- Pending exits and in-flight obligations straddle two managers; both must be monitored until old obligations zero out.
- Governance executing `migrate` holds total custody for the transition window — a single transaction of maximal trust.

## How It Works

Pause old and new entrypoints, transfer backing stake into the successor without minting new user shares, compare exchange rates, then switch managers:

```solidity
function migrate(address oldManager, address newManager) external onlyGovernance {
    _pause(oldManager);
    _pause(newManager);
    uint256 oldRate = oldManager.exchangeRate();
    oldManager.delegateWithoutMinting(newManager, oldManager.totalBacking());
    require(_withinTolerance(newManager.exchangeRate(), oldRate), "rate drift");
    token.setManager(newManager);
    _unpause(newManager);
}
```

## Key Points

- Pause all mint, burn, deposit, and withdrawal paths during the custody handoff.
- Move backing without minting or burning user supply.
- Assert exchange-rate equality within explicit rounding tolerance.
- Publish the cutover boundary and pending-exit treatment.
- Monitor both old and new managers until old obligations are zero.

## Source Evidence

- Stader BNBx includes migration tests around moving funds into a successor manager without minting and preserving exchange-rate assumptions during token-manager cutover.

## Related Patterns

- [Operator-Routed Liquid Staking Share](./pattern-operator-routed-liquid-staking-share.md)
- [Permissioned Exit Custody](../../ANTIPATTERNS.md#permissioned-exit-custody)
