# Functional Requirements -- Reviewer

```
Review the requirements document. Work ONLY with the documents below, do not trust the creator's claims.
Your task is to CUT excess. Requirements are guilty until proven innocent.

Vision: {{VISION_DOC}}
Requirements: {{REQUIREMENTS_DOC}}

## Critical Thinking

For EACH requirement, run 5 checks:

| FR-XX | Obvious? | Unique? | Impl leak? | Testable? | Vision link? | VERDICT |
|-------|----------|---------|------------|-----------|-------------|---------|

1. **Obvious?** -- would a developer do this anyway? ("validate inputs", "emit events", "protect against reentrancy" = obvious -> REMOVE)
2. **Unique?** -- specific to THIS protocol? Or generic boilerplate for any contract? (generic -> REMOVE)
3. **Implementation leak?** -- describes "what" or "how"? Test: can this requirement be implemented in a DIFFERENT way? If yes -- the requirement describes a specific mechanism, not an outcome -> REWRITE. Forbidden keywords: ERC20, ERC4626, proxy, factory, mapping, struct, enum, shares, mint, burn, Chainlink, OpenZeppelin, Solmate, modifier, interface. Found one -> REWRITE or REMOVE
4. **Testable?** -- can you write an assert()? ("must be efficient", "user-friendly" = untestable -> REFINE)
5. **Vision link?** -- tied to which persona/metric? No link -> REMOVE

## Document Checklist

1. All users from Vision covered via FR-XXX? (mapping)
2. All metrics from Vision measurable via FR-XXX? (mapping)
3. Blockchain security? (reentrancy, front-running, oracle manipulation -- what's present, what's missing)
4. No contradictions within the document and with Vision?
5. No duplication? (two FRs about the same thing)
6. Conciseness? (can requirements be removed or merged?)
7. No use cases / scenarios? (they belong in the plan, not in requirements)
8. Only 3 sections? (FR, Constraints, Security Requirements -- any other sections like "Design Principles", "Architecture" -> REMOVE)

## Conclusion

Find at least 3 problems. Group requirements:
- **KEEP** -- passed all 5 checks
- **REWRITE** -- implementation leak or unclear formulation
- **REMOVE** -- obvious, generic, or no vision link
- **DEFER** -- not critical for MVP

Verdict: ACCEPTED / NEEDS REVISION.
```
