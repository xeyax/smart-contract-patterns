# Custodial Reserve Backing Requirements

> Requirements for wrapped assets whose backing exists under off-chain or cross-chain custody.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, custodian, reserves, wrapped-asset, backing |
| Type | Requirement |

## R1: Full Backing

**Custodied backing must be greater than or equal to token supply.**

```
custody_balance >= wrapped_token_total_supply
```

### What This Means

- Every minted wrapped token has corresponding custodied backing.
- Minting requires evidence or custodian approval of received backing.
- Burns reduce token supply before or during off-chain release.

## R2: Public Verifiability

**Users and monitors can independently compare reserves and token supply.**

### What This Means

- Custody addresses, attestations, or proof reports are public.
- Token supply is queryable on-chain.
- Reserve reports identify timing and covered chains/assets.

## R3: Settlement Traceability

**Mint and burn requests have durable external settlement identifiers.**

### What This Means

- Mint requests link to incoming custody deposits.
- Burn requests link to outgoing settlement transaction ids.
- Request ids are not reused.

## R4: Operational Liveness

**The redemption process remains live under normal operating constraints.**

### What This Means

- Minimum redemption sizes or batching prevent dust operational DoS.
- Pauses do not permanently block settlement or refunds.
- Custodian and merchant roles have documented fallback procedures.

## R5: Reserve-Gated Minting Fails Closed

**When minting is reserve-gated, stale, missing, or insufficient reserve data blocks new minting.**

### What This Means

- Reserve and supply feeds have explicit freshness windows.
- Reserve and supply decimals are normalized before comparing backing.
- Missing feed configuration is documented as operational backing, not enforced on-chain backing.
- Failing reserve checks block minting but do not silently bless undercollateralized supply.

## R6: Signing Policy Respects Reserve Limits

**When reserve enforcement happens in a signer or custodian layer, signers must reject mint or withdrawal requests that exceed configured reserve, cap, or fee constraints before producing approvals.**

### What This Means

- Signer-side caps are documented as off-chain or committee-enforced controls.
- Tests cover over-cap minting, withdrawal fee bounds, and insufficient reserve cases.
- Users can distinguish on-chain proof of backing from signer-side policy checks.

## R7: Migration Preserves Backing

**Bridge migration, blocked-fund destruction, and local supply mutation must preserve the relationship between outstanding wrapped supply and claimable reserves.**

### What This Means

- Migration receivers are new adapters, lockboxes, or user-claim contracts, not operator wallets without claim semantics.
- Local burns and blocked-fund destruction are reconciled against outstanding supply and pending exits.
- New mint and burn roles are activated only after reserve, peer, and migration boundaries are verified.

## Source Evidence

- Stacks sBTC signer validation checks mint and withdrawal limits before signing in `/private/tmp/defillama-source/stacks-network__sbtc/signer/src/bitcoin/validation.rs`, with limit tests in the same tree.
- USDT0 audit reports discuss child-token supply mutation, bridge migration receivers, and reserve/backing preservation during OFT and adapter migrations; this is lower-confidence audit-source evidence because no implementation code was present in the inspected repository.

## Related Patterns

- [Custodian-Attested Mint/Burn](./pattern-custodian-attested-mint-burn.md)
- [Signed Custody-Routed Mint](./pattern-signed-custody-routed-mint.md)
- [Bridge Custodian Concentration](../../ANTIPATTERNS.md#bridge-custodian-concentration)
