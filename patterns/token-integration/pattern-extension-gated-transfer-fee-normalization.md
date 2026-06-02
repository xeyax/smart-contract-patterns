# Extension-Gated Transfer-Fee Normalization

> Support deterministic token-program transfer fees by reading canonical extension state, normalizing included/excluded amounts, and rejecting unsupported extensions.

## Metadata

| Property | Value |
|----------|-------|
| Category | token-integration |
| Tags | token, token-2022, transfer-fee, normalization, solana |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- The token program exposes canonical, inspectable transfer-fee extension state
- Fees are deterministic from mint configuration and transfer amount
- AMM or vault math needs to quote gross and net amounts consistently
- Unsupported token extensions can be rejected at onboarding

## Avoid When

- Fees are arbitrary, upgradeable, or hidden behind external token code
- Transfer hooks can mutate balances or call back into protocol state
- The protocol cannot read extension configuration on-chain
- Slippage checks use requested amounts instead of normalized received amounts

## How It Works

Convert between amount-before-fee and amount-after-fee using the token program's canonical fee configuration:

```rust
let fee_config = read_transfer_fee_extension(mint)?;
let amount_after_fee = fee_config.calculate_post_fee_amount(amount_before_fee)?;
let amount_before_fee = fee_config.calculate_pre_fee_amount(amount_after_fee)?;
```

At onboarding, reject unsupported extensions or require an admin badge/allowlist for the exact mint behavior.

## Key Points

- This is a narrow exception to generic fee-on-transfer rejection.
- Read canonical token-program extension state; do not infer fees from off-chain metadata.
- Reject unsupported extensions such as unsafe hooks, confidential behavior, or mutable fee models.
- Badge or allowlist exceptional token extensions explicitly, and reject native mints or freeze authorities when they violate the pool's policy.
- Verify inverse fee math and rounding direction.
- Apply user slippage limits to normalized amounts, including partial-fill swaps where only the used input should be converted back to fee-included amount.
- Keep post-transfer balance reconciliation for integrations where external balance changes are possible.
- If Token-2022 transfer hooks are supported, derive and validate the exact remaining-account slice required by the hook before calling transfer CPI; fee normalization alone does not make hook behavior safe.
- For escrow lifecycles, gross up locked amounts for transfer fees and harvest withheld fees before closing accounts.

## Source Evidence

- Loopscale's cloned DAMM v2 source reads Token-2022 transfer-fee extension state, normalizes swap and liquidity amounts around included/excluded fees, rejects unsupported extensions, and tests fee-aware swap/liquidity paths.
- Orca Whirlpools rejects unsupported Token-2022 extensions, native mints, and freeze authorities unless badge policy allows them in `/private/tmp/defillama-source/orca-so__whirlpools/programs/whirlpool/src/util/v2/token.rs`, and stores badge policy in `state/token_badge.rs`.
- Orca Whirlpools normalizes transfer-fee excluded and included amounts in `util/v2/token.rs`.
- Meteora DAMM v2 normalizes transfer-fee amounts for exact-in, partial-fill, and exact-out swaps in `/private/tmp/defillama-source/MeteoraAg__damm-v2/programs/cp-amm/src/instructions/swap`.
- Jupiter Lock rejects unsupported Token-2022 extensions, computes pre-fee and post-fee escrow transfers, routes transfer-hook remaining accounts, emits memos, and harvests withheld fees before account close in `/private/tmp/defillama-source/jup-ag_jup-lock/programs/locker/src/util/token2022.rs`.
- Meteora Presale declares and parses Token-2022 hook remaining-account slices before deposits in `/private/tmp/defillama-source/MeteoraAg_presale/programs/presale/src/token2022.rs`.

## Related Patterns

- [Balance Delta Transfer Accounting](./pattern-balance-delta-transfer-accounting.md)
- [Full-Precision Directed Rounding](../math/pattern-full-precision-directed-rounding.md)
- [Fee-on-Transfer Blindness](../../ANTIPATTERNS.md#fee-on-transfer-blindness)
