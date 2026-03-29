# Contracts Formatting Rules

Rules for `contracts.md` artifact.

## State variables

Use consistent annotation style: `name -- description (constraints)`.

Constraints in parentheses at end, always include mutability:

```markdown
- baseVault -- address of the underlying ERC-4626 vault (immutable)
- performanceFeeBps -- current fee rate in basis points (mutable, capped at 3000)
- highWaterMark -- global PPS high-water mark (mutable, never decreases, starts at 1e18)
- referrer -- mapping user → referrer address (set once, immutable per user)
```

Mutability categories: `immutable`, `mutable` (optionally with constraint), `set once`.
