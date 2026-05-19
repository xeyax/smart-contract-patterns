# Solana Account Cohort Validation

> Validate every passed Solana account as part of the expected account cohort before trusting its data, authority, or balance.

## Metadata

| Property | Value |
|----------|-------|
| Category | access-control |
| Tags | solana, account-validation, pda, token-account, cohort |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | High |

## Use When

- A Solana instruction receives many accounts from the caller
- Program logic depends on account order, role, owner, mint, or authority
- External programs such as token programs or orderbooks are integrated directly
- A later CPI or accounting step assumes account identities are coherent

## Avoid When

- Accounts are created and owned entirely inside one transaction without caller choice
- The framework already enforces every needed account relationship
- The program does not use external token or market accounts

## Trade-offs

**Pros:**
- Prevents account substitution across pools, markets, and vaults
- Makes instruction preconditions explicit and fuzzable
- Catches role confusion before value-bearing CPIs

**Cons:**
- Adds repetitive validation code if not abstracted carefully
- Requires tests for negative account permutations
- Still needs careful variable naming to avoid later role mixups

## How It Works

Validate accounts as a cohort, not as isolated types:

- account owner is the expected program
- account discriminator or layout tag matches the expected account type before raw layout parsing
- PDA address matches the seed tuple
- stored pool/reserve/market keys match the passed accounts
- SPL token mint, owner, delegate, and close authority match the role
- external orderbook or program accounts belong to the configured integration

## Key Points

- Validate role relationships before deserializing mutable state for execution.
- When using raw layout parsing or bytemuck-style casts, check owner, length, and discriminator/tag before trusting fields.
- Keep helper functions role-specific; avoid generic "is valid token account" checks for custody paths.
- After validation, use names that preserve semantic account role.
- Test swapped same-type accounts, wrong mint, wrong authority, wrong market, and wrong program owner.
- Combine with post-CPI accounting checks when balances can change externally.
- Validate executable-account cohorts too: configured CPI program ids, program-data metadata where relevant, and deterministic remaining-account partitions.
- For stake and LST flows, validate account owner/type, mint/authority, and delegated stake amount against protocol records before conversion or CPI.
- When client SDKs derive large account cohorts, treat those derivations as integration assistance only; on-chain instructions still need owner, PDA, mint, authority, and suffix validation.

## Source Evidence

- Raydium AMM validates Serum/OpenBook market and open-orders accounts, pool configuration PDAs, vault owners, mints, delegates, and token authorities.
- Kamino Lend validates PDA-derived lending accounts and post-CPI token states for reserves and obligations.
- Raydium evidence also shows why later role confusion remains a risk even after initial validation.
- OnRe's Jupiter integration adapter is useful negative evidence: it length-checks and raw-parses account layouts, which should be paired with owner and discriminator checks in value-bearing programs.
- Sanctum validates configured calculator and pricing CPI programs, account suffixes, and stake-pool account owners/types for LST value calculators.
- Marinade rejects extra remaining accounts and validates stake delegation amount and validator identity against protocol records.
- Sanctum INF Jupiter integration validates expected account order and program ids for adapter calls, while Sanctum stake-pool SDK helpers show why PDA derivations and account cohort builders should remain corroborating evidence rather than replacing on-chain checks in `/private/tmp/defillama-source/igneous-labs_inf-jup-interface/jup-interface/src/lib.rs` and `/private/tmp/defillama-source/igneous-labs_sanctum-spl-stake-pool-sdk/core/src/instructions`.

## Related Patterns

- [PDA-Scoped Protocol Authority](./pattern-pda-scoped-protocol-authority.md)
- [Adapter-Isolated Core Ledger](../token-integration/pattern-adapter-isolated-core-ledger.md)
- [Account Role Confusion](../../ANTIPATTERNS.md#account-role-confusion)
