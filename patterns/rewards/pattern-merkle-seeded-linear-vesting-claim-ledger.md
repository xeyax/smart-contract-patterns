# Merkle-Seeded Linear Vesting Claim Ledger

> Use a Merkle proof once to instantiate a per-recipient claim ledger, then release the locked portion through deterministic linear vesting.

## Metadata

| Property | Value |
|----------|-------|
| Category | rewards |
| Tags | rewards, merkle, vesting, claim, clawback |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- A fixed off-chain allocation has both immediately claimable and time-vested portions
- Claim state should live in per-recipient accounts after the first Merkle verification
- The distributor needs global caps for total claims, claim count, start/end time, and clawback
- Recipients should be able to claim vested deltas without resupplying the original Merkle proof

## Avoid When

- Allocations change cumulatively across epochs
- The Merkle leaf does not domain-separate distributor, mint, version, and recipient terms
- Admins can move the enable slot or clawback time without clear governance constraints
- Off-chain tree generation is not reproducible or tested against the on-chain verifier

## Trade-offs

**Pros:**
- Pays only one Merkle verification cost per recipient
- Separates initial proof validation from later vested claims
- Makes claimed unlocked and claimed locked amounts auditable per recipient

**Cons:**
- Creates persistent per-recipient state
- Off-chain tree mistakes become hard to repair after claims begin
- Clawback and enable-slot controls are economically sensitive admin powers

## How It Works

The distributor stores a Merkle root, token mint, vesting window, claim caps, and clawback parameters. A recipient's first claim verifies a leaf that includes the recipient allocation, creates a claim-status account, and pays the unlocked amount. Later claims compute the linearly vested locked amount, subtract the locked amount already withdrawn, and pay only the delta.

```rust
fn new_claim(ctx: Context<NewClaim>, proof: Vec<[u8; 32]>, leaf: Leaf) -> Result<()> {
    verify_merkle_proof(ctx.accounts.distributor.root, &proof, leaf.hash())?;

    ctx.accounts.claim_status.unlocked_claimed = leaf.unlocked_amount;
    ctx.accounts.claim_status.locked_total = leaf.locked_amount;
    ctx.accounts.claim_status.locked_claimed = 0;
    transfer_unlocked(leaf.unlocked_amount)?;
    Ok(())
}

fn claim_locked(ctx: Context<ClaimLocked>, now: i64) -> Result<()> {
    let vested = linear_vested(ctx.accounts.claim_status.locked_total, now);
    let amount = vested - ctx.accounts.claim_status.locked_claimed;

    ctx.accounts.claim_status.locked_claimed = vested;
    transfer_locked_delta(amount)?;
    Ok(())
}
```

## Key Points

- Domain-separate the leaf with distributor, mint, version, recipient, and allocation fields.
- Store per-recipient claimed unlocked amount, total locked amount, and claimed locked amount.
- Cap total claimed tokens and total claim nodes against the distributor configuration.
- Reject claims before enablement and after terminal clawback state when applicable.
- Make clawback and enable-slot changes explicit governance actions.
- Keep off-chain tree generation deterministic and covered by fixtures that match on-chain hashing.

## Source Evidence

- Kamino Distributor stores distributor caps, Merkle root, vesting window, and clawback parameters in [`programs/merkle-distributor/src/state/merkle_distributor.rs`](https://github.com/Kamino-Finance/distributor/blob/aecda23a7363f448fae37543ab5a9f4662e50e50/programs/merkle-distributor/src/state/merkle_distributor.rs).
- Kamino Distributor initializes distributor state and verifies new claims in [`programs/merkle-distributor/src/instructions/new_distributor.rs`](https://github.com/Kamino-Finance/distributor/blob/aecda23a7363f448fae37543ab5a9f4662e50e50/programs/merkle-distributor/src/instructions/new_distributor.rs) and `instructions/new_claim.rs`.
- Kamino Distributor tracks per-recipient claim status and locked-claim deltas in [`programs/merkle-distributor/src/state/claim_status.rs`](https://github.com/Kamino-Finance/distributor/blob/aecda23a7363f448fae37543ab5a9f4662e50e50/programs/merkle-distributor/src/state/claim_status.rs) and `instructions/claim_locked.rs`.
- Kamino Distributor implements clawback behavior in [`programs/merkle-distributor/src/instructions/clawback.rs`](https://github.com/Kamino-Finance/distributor/blob/aecda23a7363f448fae37543ab5a9f4662e50e50/programs/merkle-distributor/src/instructions/clawback.rs).

## Related Patterns

- [Indexed Merkle Airdrop](./pattern-indexed-merkle-airdrop.md)
- [Merkle-Instantiated Vesting Escrow Factory](./pattern-merkle-instantiated-vesting-escrow-factory.md)
- [Isolated Vesting Schedule Escrow](./pattern-isolated-vesting-schedule-escrow.md)
- [Delayed Cumulative Merkle Claims](./pattern-delayed-cumulative-merkle-claims.md)
