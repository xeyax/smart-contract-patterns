# Extension-Gated Transfer-Fee Normalization

> Support deterministic token-program transfer fees by reading canonical extension state, normalizing included/excluded amounts, and rejecting unsupported extensions.

## Metadata

| Property | Value |
|----------|-------|
| Category | token-integration |
| Platform | solana |
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

## Trade-offs

**Pros:**
- Unlocks deterministic transfer-fee tokens that blanket fee-on-transfer rejection would exclude.
- Fees are read from canonical on-chain extension state — no trust in off-chain metadata or token-code claims.
- Gross/net normalization keeps quotes, slippage checks, and liquidity math consistent on both sides of the fee.
- Onboarding rejection and badge policy contain the exception to explicitly reviewed mints.

**Cons:**
- Inverse fee math (pre-fee from post-fee) has rounding pitfalls in both directions; off-by-one errors leak value at volume.
- Fee configuration can change between reads; stale assumptions misprice transfers and escrow amounts.
- Badge/allowlist administration is ongoing operational work and a standing misconfiguration risk.
- Partial-fill paths must convert only the used input back to fee-included amounts — an easy slippage-accounting mistake.
- Covers only deterministic fees: transfer hooks and escrow lifecycles (gross-up, withheld-fee harvest before close) still need separate handling.

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
- Orca Whirlpools rejects unsupported Token-2022 extensions, native mints, and freeze authorities unless badge policy allows them in [`programs/whirlpool/src/util/v2/token.rs`](https://github.com/orca-so/whirlpools/blob/a119d79bada4e730fef791cac6adb669405a21de/programs/whirlpool/src/util/v2/token.rs), and stores badge policy in `state/token_badge.rs`.
- Orca Whirlpools normalizes transfer-fee excluded and included amounts in `util/v2/token.rs`.
- Meteora DAMM v2 normalizes transfer-fee amounts for exact-in, partial-fill, and exact-out swaps in [`programs/cp-amm/src/instructions/swap`](https://github.com/MeteoraAg/damm-v2/blob/58a13fcf45516a9f27f2bd2a2056fb66673454e0/programs/cp-amm/src/instructions/swap).
- Jupiter Lock rejects unsupported Token-2022 extensions, computes pre-fee and post-fee escrow transfers, routes transfer-hook remaining accounts, emits memos, and harvests withheld fees before account close in [`programs/locker/src/util/token2022.rs`](https://github.com/jup-ag/jup-lock/blob/f1535b4067b1d90fd682edc94ac693496b0a9812/programs/locker/src/util/token2022.rs).
- Meteora Presale declares and parses Token-2022 hook remaining-account slices before deposits in [`programs/presale/src/token2022.rs`](https://github.com/MeteoraAg/presale/blob/2acd7c9c20bada425e9ff493260be4328b350b57/programs/presale/src/token2022.rs).

## Related Patterns

- [Balance Delta Transfer Accounting](./pattern-balance-delta-transfer-accounting.md)
- [Full-Precision Directed Rounding](../math/pattern-full-precision-directed-rounding.md)
- [Fee-on-Transfer Blindness](../../ANTIPATTERNS.md#fee-on-transfer-blindness)
