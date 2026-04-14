# glossary.md formatting rules

## Structure

```markdown
# Glossary

| Term | Definition | Source |
|------|------------|--------|
| Session | Bounded library use context, opened per user interaction and closed afterwards | Purpose |
| Cache | In-process store of previously computed results, reusable for matching subsequent inputs | inferred from FR-008 |
| Extension | User-provided implementation that the library invokes through a documented contract | Purpose |
| Token | Smallest atomic input unit produced by the parsing layer | — [GAP]: term used in FR-004, no definition |
```

## Rules

- Alphabetical order.
- One row per term.
- "Source" column: `Purpose`, `Glossary section`, `inferred from FR-NN`, or `—` (with a `[GAP]` if undefined).
- Skip generic English (`user`, `system`) and unambiguous standards (`HTTP`, `JSON`, `ERC-20`).
