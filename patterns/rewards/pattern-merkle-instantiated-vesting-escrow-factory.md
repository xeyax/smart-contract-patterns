# Merkle-Instantiated Vesting Escrow Factory

> Commit a bulk vesting distribution with one Merkle root, then let each recipient instantiate an isolated vesting escrow from a proven leaf.

## Metadata

| Property | Value |
|----------|-------|
| Category | rewards |
| Tags | rewards, vesting, merkle, escrow, factory |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- A large vesting distribution should avoid pre-creating every escrow
- Each recipient needs an independently claimable and revocable schedule
- The allocation set is fixed before deposits are funded
- Off-chain allocation generation can publish proofs and totals for review

## Avoid When

- Allocations update continuously or need cumulative top-ups
- Recipients should share one global vesting curve
- The tree generator cannot prevent duplicate recipient leaves
- Escrow creation must be impossible after a short campaign window

## Trade-offs

**Pros:**
- Avoids the upfront cost of creating every schedule
- Keeps each vesting grant isolated after instantiation
- Lets recipients or third parties create only the escrows that are needed

**Cons:**
- The off-chain tree generator becomes part of the distribution boundary
- Duplicate or malformed leaves can create ambiguous entitlements
- Uninstantiated allocations need an explicit expiry and recovery policy

## How It Works

Create a root escrow that stores the token mint, authority, Merkle root, and aggregate funding. A recipient proves a leaf that binds the root escrow, recipient, amount, vesting schedule, and optional capability bits. The factory then creates a deterministic child escrow PDA or contract for that recipient.

```rust
fn create_vesting_from_root(ctx: Context, leaf: VestingLeaf, proof: Vec<[u8; 32]>) -> Result<()> {
    require!(verify_merkle_proof(root.root_hash, leaf.hash(), proof), "bad proof");

    let escrow = derive_escrow_address(root.key(), leaf.recipient);
    require!(!escrow.initialized, "already created");

    escrow.recipient = leaf.recipient;
    escrow.amount = leaf.amount;
    escrow.schedule = leaf.schedule;
    escrow.root = root.key();
}
```

Use domain-separated hashes for leaves and internal nodes so a leaf cannot be reinterpreted as an internal branch.

## Implementation

### Key Points

- Bind the root escrow address into the child escrow derivation.
- Include recipient, token, amount, schedule parameters, and permission bits in the leaf.
- Domain-separate leaf and internal node hashes.
- Track whether a child escrow has already been created for the leaf.
- Publish the claim data and aggregate token total before funding or activation.
- Define expiry and recovery for allocations that are never instantiated.

## Source Evidence

- Jupiter Lock stores root escrow state in `/private/tmp/defillama-source/jup-ag_jup-lock/programs/locker/src/state/root_escrow.rs`, creates root escrows in `instructions/root_escrow_instructions/create_root_escrow.rs`, and instantiates recipient vesting escrows from Merkle proofs in `instructions/root_escrow_instructions/create_vesting_escrow_from_root.rs`.
- Jupiter Lock domain-separates Merkle tree leaves and internal nodes in `/private/tmp/defillama-source/jup-ag_jup-lock/merkle-tree/src/merkle_tree.rs` and `merkle-tree/src/jup_lock_merkle_tree.rs`.

## Real-World Examples

- Jupiter Lock uses a root escrow plus Merkle proofs to create recipient-scoped vesting escrows lazily.

## Related Patterns

- [Indexed Merkle Airdrop](./pattern-indexed-merkle-airdrop.md)
- [Isolated Vesting Schedule Escrow](./pattern-isolated-vesting-schedule-escrow.md)
- [Participant Permission Bitmap](../access-control/pattern-participant-permission-bitmap.md)

## References

- See Source Evidence.
