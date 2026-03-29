# Invariants Formatting Rules

Rules for `invariants.md` artifact.

## Format

```markdown
- I{N}: **{Name}** -- {description}.
```

## Numbering

Sequential across all contracts in the file (not per-contract). If VaultFeeWrapper has I1–I15, SimpleFeeReceiver starts at I16.

## Content

- Each invariant = one line, plain English.
- Only list invariants the contract must actively enforce. Exclude platform guarantees (EVM atomicity, overflow protection, msg.sender identity).
