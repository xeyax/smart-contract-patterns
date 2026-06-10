# PDA-Scoped Protocol Authority

> Derive Solana protocol authorities and custody accounts from canonical PDA seeds, then verify every account against the stored authority graph.

## Metadata

| Property | Value |
|----------|-------|
| Category | access-control |
| Platform | solana |
| Tags | solana, pda, authority, custody, account-validation |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | High |

## Use When

- A Solana program owns token vaults, mints, obligations, or market authority through PDAs
- CPI signing uses program-derived seeds and bumps
- Account addresses must be reproducible by clients and tests
- Custody safety depends on stored account relationships

## Avoid When

- Authority is intentionally held by an external signer or multisig
- PDA seeds are not stable across upgrades
- The program cannot verify passed accounts against canonical derivations

## Trade-offs

**Pros:**
- Removes private-key custody for protocol-owned accounts
- Makes authority addresses deterministic and testable
- Reduces account substitution risk when combined with strict constraints

**Cons:**
- Seed design becomes part of the security boundary
- Seed or bump migrations are hard after deployment
- PDA checks do not replace post-CPI balance and owner reconciliation

## How It Works

Define seed formulas for every protocol authority and custody account. Store canonical addresses where needed, then verify passed accounts before mutating state or signing CPI calls.

```rust
let expected_vault = Pubkey::find_program_address(
    &[b"vault", market.key().as_ref(), reserve.key().as_ref()],
    program_id,
).0;

require_keys_eq!(expected_vault, vault.key(), ErrorCode::InvalidVault);
```

## Key Points

- Use distinct seed prefixes for each account role.
- Store and verify bumps or derive them consistently.
- Verify account owner, mint, token authority, and close authority in addition to PDA address.
- Sign CPIs only with the seed tuple that derives the expected authority.
- For hot Solana accounts, precompute a bounded set of equivalent authority PDAs and require the route or instruction to name which shard is being used.
- Reconcile internal accounting after token CPIs.

## Source Evidence

- Kamino Lend derives market, reserve, obligation, vault, and collateral accounts through helper PDA functions.
- Its handlers and transfer utilities verify canonical account relationships before CPI signing.
- Post-transfer checks reconcile vault balances and internal ledger state after token CPIs.
- Jupiter routing code uses multiple equivalent authority PDAs to avoid hot-account contention, with account indexes selected by the swap transaction builder in [`jupiter-core/src/swap_transaction/build_swap_instruction.rs`](https://github.com/jup-ag/jupiter-amm-implementation/blob/cc068c9d1df0060c62f9a8a4fc37ea13ea7b9b39/jupiter-core/src/swap_transaction/build_swap_instruction.rs) and authority definitions shared with [`src/lib.rs`](https://github.com/jup-ag/jupiter-cpi/blob/12bc5f67b94a2c3edc74d6e721a19442124a0bad/src/lib.rs).

## Related Patterns

- [Solana Account Cohort Validation](./pattern-solana-account-cohort-validation.md)
- [Balance Delta Transfer Accounting](../token-integration/pattern-balance-delta-transfer-accounting.md)
- [Two-Step Authority Handoff](./pattern-two-step-authority-handoff.md)
