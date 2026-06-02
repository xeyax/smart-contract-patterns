# Supply-Referenced Veto Support Drift

> Veto support based on token supply or withdrawal claims can drift as rebases, wrapping, finalization, and denominator changes occur.

## Metadata

| Property | Value |
|----------|-------|
| Category | governance |
| Tags | governance, veto, supply, rebase, denominator |
| Type | Risk Description |

## Applies When

- Veto support is measured as a percentage of token supply, shares, or withdrawal claims
- The underlying token rebases or has wrapper conversions
- Withdrawal requests move between pending, finalized, and claimable states
- Support thresholds determine proposal delays or rage-quit activation

## Requirements Affected

- Governance thresholds need stable, auditable denominators.
- Support changes caused by token mechanics should not surprise proposal state transitions.

## Failure Modes

- Rebases change total supply and move support across a threshold without new stakeholder intent.
- Finalized withdrawals leave the denominator while claims remain in a signaling escrow.
- Wrapped and unwrapped representations are double-counted or undercounted.

## Mitigations

- Define denominator sources for every veto state.
- Snapshot support at activation boundaries when appropriate.
- Normalize wrapped, unwrapped, pending, and claimable balances exactly once.
- Test threshold crossings across rebases, finalizations, and claim transitions.

## Source Evidence

- Lido Dual Governance has to account for stETH supply, withdrawal-claim state, and escrowed support when determining veto state transitions.

## Related Patterns

- [Stakeholder-Extensible Governance Timelock](./pattern-stakeholder-extensible-governance-timelock.md)
- [Veto Governance Liveness And Exit Safety Requirements](./req-veto-governance-liveness-and-exit-safety.md)
