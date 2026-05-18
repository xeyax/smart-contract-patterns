# Bridge Exit Liveness Requirements

> Requirements that keep already-escrowed, burned, or proven bridge assets claimable through pauses, failures, and migrations.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, liveness, pause, refund, migration |
| Type | Requirement |

## R1: Pauses Preserve Safe Exit Paths

**Pausing new bridge inflows should not automatically pause withdrawals, refunds, or already-proven exits.**

### What This Means

- Deposit pause and exit pause are separate controls.
- If all exits cannot remain open, the safest solvent exit path stays available.
- Emergency playbooks explain when and why an exit pause can be used.

## R2: Failed Destination Settlement Has A Refund Path

**If a destination token, peer, or gateway validation fails, users can recover source value through an authenticated refund path.**

### What This Means

- Destination finalization fails closed instead of minting into invalid mappings.
- Refund messages are replay-safe and authenticated by the bridge.
- Refunds remain callable while new deposits are paused.

## R3: Migration Accounts For In-Flight Messages

**Bridge migration must account for pending retryables, proofs, exits, and delayed messages before burning escrow or removing mint authority.**

### What This Means

- Operators define a final accepted source boundary.
- Pending messages are completed, refunded, or made claimable elsewhere.
- Custody or mint authority moves only after the old bridge's obligations are bounded.

## R4: Admin Overrides Are Explicitly Trusted

**Owner or governance override paths that can force registration, burn custody, or move bridge roles must be documented as trusted paths.**

### What This Means

- Override events include token, gateway, peer, and amount fields.
- Monitoring can detect changes that strand pending exits.
- Tests cover override misuse around in-flight settlement.

## Source Evidence

- Arbitrum token bridge pauses deposits while preserving L1 withdrawal finalization paths.
- Arbitrum gateway fallback handlers issue refund withdrawals when destination token validation fails.
- Arbitrum native USDC migration tests check pending deposits before burn and role transfer.

## Related Patterns

- [Escrow Mint-Burn Refund Fallback](./pattern-escrow-mint-burn-refund-fallback.md)
- [Proof Bridge Exit Safety Requirements](./req-proof-bridge-exit-safety.md)
- [Pause Traps Funds](../../ANTIPATTERNS.md#pause-traps-funds)
