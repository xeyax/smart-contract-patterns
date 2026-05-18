# Tiered Loss Waterfall Requirements

> Requirements for vault systems that intentionally allocate losses across senior and junior risk classes instead of pro-rata across all holders.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, loss, waterfall, tranche, buffer |
| Type | Requirement |

## R1: Loss Priority Is Explicit

**Every loss must move through a documented priority order before senior share price is reduced.**

### What This Means

- Safety buffers, locked users, stakers, and senior holders have an ordered loss sequence.
- The order is visible to users before they enter a risk class.
- Tests cover losses that stop at each tier and losses that overflow multiple tiers.

## R2: Tier Capacity Is Measurable

**Each loss tier must expose how much loss it can absorb before the next tier is touched.**

### What This Means

- Buffer balances, locked balances, staked balances, and senior supply are measurable.
- Accounting cannot double-count the same assets in two tiers.
- Small losses and large losses use the same deterministic waterfall.

## R3: Junior Risk Is Opt-In

**Users assigned to first-loss or junior tiers must opt into that risk class through clear mechanics.**

### What This Means

- Locked, staked, or junior positions are distinct from senior receipt tokens.
- Conversions between tiers are explicit and cannot be forced by ordinary admin action.
- Exit rules define whether pending exits still absorb losses.

## R4: Waterfall Execution Preserves Solvency

**Applying a loss must update buffers, tier balances, and senior price atomically and without leaving hidden debt.**

### What This Means

- Loss application emits enough data to reconstruct which tiers absorbed loss.
- Rounding favors solvency over over-crediting any tier.
- Pauses do not hide pending loss realization.

## Source Evidence

- infiniFi's yield-sharing accounting applies losses first to a safety buffer, then locked users, then staked users, and finally senior receipt-token price, with unit tests for each tier transition.

## Related Patterns

- [Vault Fairness Requirements](./req-vault-fairness.md)
- [Liquid Staking Loss Accounting Requirements](./req-liquid-staking-loss-accounting.md)
- [Credit Loss Accounting Requirements](../lending/req-credit-loss-accounting.md)
