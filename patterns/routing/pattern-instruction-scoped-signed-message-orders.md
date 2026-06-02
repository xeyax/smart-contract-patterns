# Instruction-Scoped Signed Message Orders

> Verify signed order messages against the exact instruction, signer, payload fields, expiry, and replay cache before settlement.

## Metadata

| Property | Value |
|----------|-------|
| Category | routing |
| Tags | routing, signed-order, ed25519, solana, replay |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Orders are signed off-chain but verified inside an execution instruction
- The chain exposes signature-verification instructions or precompiles
- Settlement must bind taker, delegate, slot, uuid, market, side, price, and size
- Replay state can be bounded per signing account

## Avoid When

- The signed payload omits value-bearing order or settlement fields
- Instruction offsets or message bytes cannot be verified in-program
- Replay protection is only off-chain
- The replay cache can grow without bounds

## Trade-offs

**Pros:**
- Keeps off-chain order UX while preserving in-program settlement checks
- Prevents signature reuse across instructions or settlement contexts
- Works for non-EVM signature systems without forcing EIP-712 terminology

**Cons:**
- Verification depends on instruction ordering and offset correctness
- Replay caches need bounded storage and eviction rules
- Message serialization must remain stable across client versions

## How It Works

The settlement instruction reads the signature-verification instruction, confirms
the signer and message offsets, parses the typed payload, validates expiry and
taker/delegate scope, then records a bounded uuid or order id before settlement.

```rust
fn settle_signed_order(ctx: Context, order: SignedOrder) {
    verify_ed25519_instruction(
        ctx.instructions,
        order.signer,
        order.message_bytes,
        order.signature,
    )?;

    require!(order.slot_expiry >= current_slot(), "expired");
    require!(order.taker == ctx.taker || order.delegate == ctx.taker, "taker");
    replay_cache.insert(order.signer, order.uuid)?;

    settle(order);
}
```

### Adjacent-Instruction Settlement Guard Variant

For Solana protocol zaps or aggregator settlements that do not carry a signed order, the program can still bind settlement to the surrounding transaction. Inspect the adjacent instruction, verify the expected program id and account layout, and require the settlement instruction to be paired with the exact protocol-zap instruction that produced the assets.

This is narrower than signed-order verification. It prevents orphaned settlement calls and account substitution, but it does not replace user slippage bounds inside the routed swap or liquidity leg.

## Implementation

- Verify signature instruction program id, offsets, signer, signature, and exact message bytes.
- Bind every economically relevant field in the typed payload.
- Enforce slot or timestamp expiry.
- Track replay ids on-chain with a documented bounded cache size.
- Bind taker and delegate semantics before settlement.
- When using adjacent-instruction guards, verify program id, instruction index, account order, vault accounts, and expected authority before settling.
- Test offset spoofing, wrong signer, byte mutation, expired slot, replay, and cache rollover.

## Source Evidence

- Drift validates Solana Ed25519 instruction offsets, signer, and message bytes in `/private/tmp/defillama-source/drift-labs__protocol-v2/programs/drift/src/validation/sig_verification.rs`.
- Drift binds signed message order fields and slot expiry in `programs/drift/src/state/order_params.rs`, stores a bounded replay cache in `programs/drift/src/state/signed_msg_user.rs`, and settles signed orders in `programs/drift/src/instructions/keeper.rs`.
- Drift tests signed-message replay behavior in `programs/drift/src/state/signed_msg_user/tests.rs`.
- Meteora Protocol Zap verifies adjacent instruction context and expected accounts before settlement in `/private/tmp/defillama-source/MeteoraAg_zap-program/protocol-zap/src/utils/mod.rs` and `processors/jup_v6_zap.rs`.

## Real-World Examples

- Drift Protocol settles off-chain signed Solana orders by validating Ed25519 instruction context, typed payload fields, expiry, taker/delegate scope, and replay ids.

## Related Patterns

- [Typed Signed Order Settlement](./pattern-typed-signed-order-settlement.md)
- [Signature Scope Drift](../../ANTIPATTERNS.md#signature-scope-drift)
- [Zero-Consideration Signed Order Risk](./risk-zero-consideration-signed-order.md)

## References

- Drift Protocol signed-message order source.
