# Token-2022 Transfer Hook Policy Gate

> Use Solana Token-2022 transfer hooks and extra account metadata to enforce policy state on every token transfer.

## Metadata

| Property | Value |
|----------|-------|
| Category | tokens |
| Platform | solana |
| Tags | solana, token-2022, transfer-hook, pda, compliance |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- A token needs transfer-time policy checks such as pause, allowlist, or compliance gates
- The policy state can be represented by PDAs included through `ExtraAccountMetaList`
- Wallets and integrations can support Token-2022 transfer-hook accounts
- Pausing transfers is intentionally part of the token's risk model

## Avoid When

- The token must remain ERC20-like or Token Program compatible without extra accounts
- Transfer liveness must be independent of an admin-controlled policy PDA
- Users need guaranteed exits even while ordinary transfers are paused
- Integrations cannot reliably supply the required extra accounts

## Trade-offs

**Pros:**
- Makes transfer policy executable on every transfer
- Uses PDA account validation instead of off-chain compliance promises
- Can share one policy account across a mint's transfers

**Cons:**
- Transfer integrations must include the extra-account metadata path
- Admin-controlled pause can trap transfers
- Hook program bugs can affect every token movement

## How It Works

Initialize the mint's extra-account metadata with the policy PDA required by the hook:

```rust
ExtraAccountMetaList::init::<ExecuteInstruction>(
    &mut extra_account_meta_list.try_borrow_mut_data()?,
    &[ExtraAccountMeta::new_with_seeds(&[Seed::Literal { bytes: b"pause".to_vec() }], false, true)?],
)?;
```

The hook then validates the provided accounts and checks policy state:

```rust
pub fn transfer_hook(ctx: Context<TransferHook>, amount: u64) -> Result<()> {
    require!(!ctx.accounts.pause.state, Error::Paused);
    Ok(())
}
```

## Implementation

### Key Points
- Derive policy accounts from stable seeds and validate them in the hook context.
- Initialize `ExtraAccountMetaList` before expecting wallet or program transfers to work.
- Keep admin authority explicit and preferably multisig or governance-controlled.
- Document whether pause affects transfers only, mint/burn, or off-chain redemption.
- Test missing extra accounts, wrong mint, wrong owner, pause state, unauthorized admin updates, and frozen accounts.
- Pair transfer pauses with a separate emergency redemption or book-entry process when user exit liveness matters.
- When another program transfers hook-enabled tokens, define typed remaining-account slices per transfer leg and reject malformed or unsupported extension combinations before CPI.

## Source Evidence

- OpenEden's Solana TBILL program initializes Token-2022 extra-account metadata, dispatches transfer-hook calls through fallback decoding, and checks a pause PDA during transfers in [`programs/tbill/src/lib.rs`](https://github.com/OpenEdenHQ/openeden.tbill.solana/blob/948bb2bb1c224c51ef7aeec7fc1d2bee3dcc24d4/programs/tbill/src/lib.rs), with Anchor tests for extra-account metadata, frozen accounts, transfers, and unauthorized mint/freeze/thaw paths.
- Jupiter Lock and Meteora Presale both parse transfer-hook remaining accounts before Token-2022 CPI in [`programs/locker/src/util/remaining_accounts.rs`](https://github.com/jup-ag/jup-lock/blob/f1535b4067b1d90fd682edc94ac693496b0a9812/programs/locker/src/util/remaining_accounts.rs) and [`programs/presale/src/token2022.rs`](https://github.com/MeteoraAg/presale/blob/2acd7c9c20bada425e9ff493260be4328b350b57/programs/presale/src/token2022.rs).

## Real-World Examples

- OpenEden TBILL Solana uses a Token-2022 transfer hook to enforce pause state during token movement.

## Related Patterns

- [Solana Account Cohort Validation](../access-control/pattern-solana-account-cohort-validation.md)
- [PDA-Scoped Protocol Authority](../access-control/pattern-pda-scoped-protocol-authority.md)
- [Extension-Gated Transfer-Fee Normalization](../token-integration/pattern-extension-gated-transfer-fee-normalization.md)
- [Pause Traps Funds](../../ANTIPATTERNS.md#pause-traps-funds)
