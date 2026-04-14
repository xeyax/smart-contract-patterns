# consistency-report.md formatting rules

## Five contradiction types

1. **Behavioral** — two items describe the same operation differently.
2. **Scope** — one item says X is in scope, another excludes it.
3. **Constraint vs FR** — Constraint forbids what FR requires.
4. **AC vs own text** — acceptance criteria contradicts the requirement text.
5. **Priority conflict** — two `Must` items cannot both be satisfied simultaneously.

## Structure

```markdown
# Consistency Report

Found N contradictions.

## Contradiction 1: Behavioral

- **Item A**: FR-001 — "User code can call any session method while the session is open"
- **Item B**: FR-005 — "Calling parse() after close() raises SessionClosedError"
- **Conflict**: FR-001 says "any method" without state qualification; FR-005 restricts a specific method by state.
- **Suggested resolution**: qualify FR-001 to "while the session is in the Open state", or surface the close-then-call exception explicitly in FR-001's acceptance criteria.

[GAP]: contradiction between FR-001 and FR-008 (behavioral)

## Contradiction 2: Constraint vs FR

...
```

If empty:
```markdown
# Consistency Report

No contradictions found across requirements.
```

## Rules

- Quote conflicting text verbatim.
- One section per contradiction. Always include all four lines: Item A, Item B, Conflict, Suggested resolution.
- One `[GAP]:` line per contradiction.
- Empty file is valid — but always include the header and summary line.
