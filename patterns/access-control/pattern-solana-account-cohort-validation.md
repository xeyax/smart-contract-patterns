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
- PDA address matches the seed tuple
- stored pool/reserve/market keys match the passed accounts
- SPL token mint, owner, delegate, and close authority match the role
- external orderbook or program accounts belong to the configured integration

## Key Points

- Validate role relationships before deserializing mutable state for execution.
- Keep helper functions role-specific; avoid generic "is valid token account" checks for custody paths.
- After validation, use names that preserve semantic account role.
- Test swapped same-type accounts, wrong mint, wrong authority, wrong market, and wrong program owner.
- Combine with post-CPI accounting checks when balances can change externally.

## Source Evidence

- Raydium AMM validates Serum/OpenBook market and open-orders accounts, pool configuration PDAs, vault owners, mints, delegates, and token authorities.
- Kamino Lend validates PDA-derived lending accounts and post-CPI token states for reserves and obligations.
- Raydium evidence also shows why later role confusion remains a risk even after initial validation.

## Related Patterns

- [PDA-Scoped Protocol Authority](./pattern-pda-scoped-protocol-authority.md)
- [Adapter-Isolated Core Ledger](../token-integration/pattern-adapter-isolated-core-ledger.md)
- [Account Role Confusion](../../ANTIPATTERNS.md#account-role-confusion)
