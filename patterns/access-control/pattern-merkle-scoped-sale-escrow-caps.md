# Merkle-Scoped Sale Escrow Caps

> Gate token-sale deposits through per-user escrows whose Merkle leaves bind owner, sale registry, and personal cap.

## Metadata

| Property | Value |
|----------|-------|
| Category | access-control |
| Tags | access-control, token-sale, merkle, escrow, cap |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- A permissioned sale needs per-user caps without storing the full allowlist on-chain
- Deposits should be isolated by sale, registry, and owner
- Users can prove their own sale eligibility at deposit time
- The off-chain allowlist can be audited before activation

## Avoid When

- Caps change continuously during the sale
- The sale cannot tolerate off-chain allowlist generation risk
- Multiple registries or sale rounds are not domain-separated
- Users need transferable eligibility

## Trade-offs

**Pros:**
- Keeps on-chain sale state compact while enforcing individual caps
- Prevents one proof from applying across unrelated sale registries
- Gives each buyer an escrow ledger for later refund or claim accounting

**Cons:**
- Tree generation and publication remain trust boundaries
- Incorrect registry binding can replay eligibility across sale rounds
- Escrow lifecycle must handle cancellation, refunds, and unclaimed balances

## How It Works

Each user creates or funds a sale escrow derived from the sale registry and owner. The deposit instruction verifies a Merkle proof whose leaf binds the owner, registry index or sale id, and personal cap. The escrow tracks cumulative deposits against that cap.

```rust
fn deposit_with_proof(ctx: Context, amount: u64, cap: u64, proof: Vec<[u8; 32]>) -> Result<()> {
    let leaf = hash_leaf(ctx.accounts.owner.key(), ctx.accounts.sale_registry.key(), cap);
    require!(verify(root, leaf, proof), "bad proof");
    require!(ctx.accounts.escrow.deposited + amount <= cap, "cap");

    transfer_quote_to_sale_vault(amount)?;
    ctx.accounts.escrow.deposited += amount;
}
```

## Implementation

### Key Points

- Derive escrow addresses from sale registry and owner.
- Include sale id, registry index, owner, and cap in the Merkle leaf.
- Domain-separate leaf and internal-node hashes.
- Track cumulative deposited amount inside the escrow.
- Define whether unused cap can be transferred, expired, or refunded.
- Test wrong registry, wrong owner, duplicate escrow, over-cap deposit, and malformed proofs.

## Source Evidence

- Meteora Presale creates permissioned escrows with Merkle proofs in `/private/tmp/defillama-source/MeteoraAg_presale/programs/presale/src/instructions/create_escrow/process_create_permissioned_escrow_with_merkle_proof.rs`.
- Its escrow state stores owner and registry information in `programs/presale/src/state/escrow.rs`, and the Merkle tree uses domain-separated node types in `/private/tmp/defillama-source/MeteoraAg_presale/merkle-tree/src/tree_node.rs` and `config_merkle_tree.rs`.

## Real-World Examples

- Meteora Presale uses Merkle proofs and per-user escrows to enforce permissioned sale caps.

## Related Patterns

- [Participant Permission Bitmap](./pattern-participant-permission-bitmap.md)
- [Indexed Merkle Airdrop](../rewards/pattern-indexed-merkle-airdrop.md)
- [Oversubscribed Pro-Rata Sale Escrow](../tokens/pattern-oversubscribed-pro-rata-sale-escrow.md)

## References

- See Source Evidence.
