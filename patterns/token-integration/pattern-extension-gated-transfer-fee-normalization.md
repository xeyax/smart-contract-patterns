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
- Verify inverse fee math and rounding direction.
- Apply user slippage limits to normalized amounts.
- Keep post-transfer balance reconciliation for integrations where external balance changes are possible.

## Source Evidence

- Loopscale's cloned DAMM v2 source reads Token-2022 transfer-fee extension state, normalizes swap and liquidity amounts around included/excluded fees, rejects unsupported extensions, and tests fee-aware swap/liquidity paths.

## Related Patterns

- [Balance Delta Transfer Accounting](./pattern-balance-delta-transfer-accounting.md)
- [Full-Precision Directed Rounding](../math/pattern-full-precision-directed-rounding.md)
- [Fee-on-Transfer Blindness](../../ANTIPATTERNS.md#fee-on-transfer-blindness)
