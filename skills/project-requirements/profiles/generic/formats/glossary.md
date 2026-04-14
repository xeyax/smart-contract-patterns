# glossary.md formatting rules

## Structure

```markdown
# Glossary

| Term | Definition | Source |
|------|------------|--------|
| Session | A bounded interaction context the system creates per user request | Purpose |
| Worker | Permissionless caller that triggers time-sensitive maintenance operations | inferred from FR-007 |
| Quota | Per-subject upper bound on resource consumption per period | — [GAP]: term used in FR-012, no definition |
```

## Rules

- Alphabetical order.
- One row per term.
- "Source" column: `Purpose`, `Glossary section`, `inferred from FR-NN`, or `—` (with a `[GAP]` if undefined).
- Skip generic English (`user`, `system`) and unambiguous standards (`HTTP`, `JSON`, `ERC-20`).
