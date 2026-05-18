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

## Related Patterns

- [Custodian-Attested Mint/Burn](./pattern-custodian-attested-mint-burn.md)
- [Signed Custody-Routed Mint](./pattern-signed-custody-routed-mint.md)
- [Bridge Custodian Concentration](../../ANTIPATTERNS.md#bridge-custodian-concentration)
