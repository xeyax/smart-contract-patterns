# Components Formatting Rules (Solidity)

Rules for the `components.md` artifact when the target language is Solidity. In this domain, a "component" is a smart **contract**; responsibilities, state variables, and interactions are described in contract terms.

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
