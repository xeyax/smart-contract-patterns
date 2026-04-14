# glossary.md formatting rules

## Structure

```markdown
# Glossary

| Term | Definition | Source |
|------|------------|--------|
| Vault | Contract holding pooled assets and issuing share tokens | Purpose |
| Keeper | Permissionless caller that triggers time-sensitive operations (rebalance, liquidation) | inferred from FR-007 |
| Drift | Difference between target and actual portfolio allocation | — [GAP]: term used in FR-012, no definition |
```

## Rules

- Alphabetical order.
- One row per term.
- "Source" column: `Purpose`, `Glossary section`, `inferred from FR-NN`, or `—` (with a `[GAP]` if undefined).
- Skip generic English (`user`, `system`) and unambiguous standards (`HTTP`, `JSON`, `ERC-20`).
