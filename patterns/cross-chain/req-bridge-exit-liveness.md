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
- Directional bridge pauses are preferable: pausing sends in one direction should not automatically block opposite-direction claims.
- If all exits cannot remain open, the safest solvent exit path stays available.
- Emergency playbooks explain when and why an exit pause can be used.

## R2: Failed Destination Settlement Has A Refund Path

**If a destination token, peer, or gateway validation fails, users can recover source value through an authenticated refund path.**

### What This Means

- Destination finalization fails closed instead of minting into invalid mappings.
- Refund messages are replay-safe and authenticated by the bridge.
- Refunds remain callable while new deposits are paused.
- Sending failed settlement funds to an admin or multisig is not a user refund path unless on-chain entitlement and claim semantics define how users recover funds.
- Split value-transfer/routing-metadata flows need recovery when value is attested or delivered but the metadata sidecar is delayed, malformed, missing, or unpaired.
- Deposit cancellation or reclaim must bind the exact message envelope and document non-refundable messaging fees.

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

## R5: Emergency Exit Pauses Are Scoped And Expiring

**A bridge that must pause proof or exit finalization needs narrow identifiers, expiry, monitoring, and a documented reason why no safer exit path can remain open.**

### What This Means

- Pause identifiers distinguish deposits, proof submission, finalization, and lockbox movement.
- Exit pauses have maximum duration or explicit renewal procedures.
- Users know whether timed-out redemptions, refunds, or standard proof-based exits remain callable.

## Source Evidence

- Arbitrum token bridge pauses deposits while preserving L1 withdrawal finalization paths.
- Arbitrum gateway fallback handlers issue refund withdrawals when destination token validation fails.
- Arbitrum native USDC migration tests check pending deposits before burn and role transfer.
- Optimism Bedrock uses scoped pause identifiers with expiry, but paused portal proof and finalization paths remain liveness exceptions that need operational justification.
- tBTC v2 redemptions include timeout paths that restore balances or keep timed-out redemptions honor-able, and optimistic mint pauses do not block standard proof-based minting.
- Tornado Nova's failed external settlement path shows why admin recovery of funds should not be treated as equivalent to user-claimable bridge refund semantics.
- Noble's CCTP metadata wrapper shows a split value-transfer and routing-metadata flow where liveness depends on pairing the sidecar metadata with the canonical value message.
- StarkGate shows delayed, depositor-only reclaim for exact bridge message envelopes, with the caveat that the remote message can still be consumed before reclaim and fees may remain spent.
- Linea message service tests show directional pause behavior where sends and claims can be paused independently in `/private/tmp/defillama-source/Consensys__linea-monorepo/contracts/test/hardhat/messaging/l1/L1MessageService.ts`.

## Related Patterns

- [Escrow Mint-Burn Refund Fallback](./pattern-escrow-mint-burn-refund-fallback.md)
- [Proof Bridge Exit Safety Requirements](./req-proof-bridge-exit-safety.md)
- [Retryable Cross-Domain Message Ledger](./pattern-retryable-cross-domain-message-ledger.md)
- [Pause Traps Funds](../../ANTIPATTERNS.md#pause-traps-funds)
