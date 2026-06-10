# Custodial Reserve Backing Requirements

> Requirements for wrapped assets whose backing exists under off-chain or cross-chain custody.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, custodian, reserve, wrapped-asset, backing |
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

## R8: Hot Redemption Buffers Are Explicit

**On-chain redeem capacity backed by a hot wallet or minting contract balance must be separated from total off-chain backing.**

### What This Means

- Users can tell whether a redeem is limited by total reserves, a hot collateral buffer, or an operator transfer from custody.
- Hot buffers have caps and replenishment procedures instead of being implied by total custodied assets.
- Off-chain hedge or custodian losses are documented as backing risks, not hidden behind successful on-chain order verification.

## R9: Off-Chain Transfer Instructions Are Solvent Before Emission

**Custodian transfer instructions must be admitted and emitted only when confirmed and escrowed funds can cover the requested amount plus fees.**

### What This Means

- Incoming custody payments are idempotently confirmed before increasing available funds.
- Pending transfer requests, escrowed funds, fees, and available funds are tracked separately.
- Emitted instructions carry sequence or payment references for reconciliation.
- Bounded processing prevents escrow or instruction queues from becoming uncallable under normal governance limits.

## Source Evidence

- Stacks sBTC signer validation checks mint and withdrawal limits before signing in [`signer/src/bitcoin/validation.rs`](https://github.com/stacks-network/sbtc/blob/a97172e25e6e255f6a973629505d400ee5d8bebf/signer/src/bitcoin/validation.rs), with limit tests in the same tree.
- USDT0 audit reports discuss child-token supply mutation, bridge migration receivers, and reserve/backing preservation during OFT and adapter migrations; this is lower-confidence audit-source evidence because no implementation code was present in the inspected repository.
- Ethena's 2023 Code4rena snapshot documents collateral sent to custodians and hedged off-chain, a limited hot collateral balance for redemptions, and custodian wallet loss as an undercollateralization risk in [`README.md`](https://github.com/code-423n4/2023-10-ethena/blob/9fd8e26fc596601c3359ceac8951740c4d5e09c7/README.md) and `contracts/README_OLD.md`.
- Flare FAssets CoreVaultManager separates available, escrowed, and pending custodian funds and tests idempotent payment confirmation plus solvency before transfer requests in [`contracts/coreVaultManager/implementation/CoreVaultManager.sol`](https://github.com/flare-foundation/fassets/blob/37c1be508a33c0d0ce31216aef45958fd4e5281e/contracts/coreVaultManager/implementation/CoreVaultManager.sol).

## Related Patterns

- [Custodian-Attested Mint/Burn](./pattern-custodian-attested-mint-burn.md)
- [Signed Custody-Routed Mint](./pattern-signed-custody-routed-mint.md)
- [Bridge Custodian Concentration](../../ANTIPATTERNS.md#bridge-custodian-concentration)
