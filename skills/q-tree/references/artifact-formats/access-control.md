# Access Control Formatting Rules

Rules for `access-control.md` artifact.

## Structure

One table per contract:

```markdown
## VaultFeeWrapper

| Function | Who can call | Guard |
|----------|-------------|-------|
| deposit(assets, receiver) | anyone | whenNotPaused, assets >= minDeposit |
| setPerformanceFee(newFeeBps) | owner | onlyOwner, newFeeBps <= 3000 |
| accruePerformanceFee() | anyone | nonReentrant |
| pause() | owner | onlyOwner |
```

## Rules

- One row per external/public function.
- Parameters use short names without types (e.g. `deposit(assets, receiver)` not `deposit(uint256, address)`).
- Guard column: modifier names and/or constraint expressions. Use code-style consistently (`onlyOwner, newFeeBps <= 3000`), not prose.
- If no guard: `—`.
