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

- **Item A**: FR-001 — "Users can submit requests anytime"
- **Item B**: FR-008 — "Submission blocked when system is halted"
- **Conflict**: FR-001's "anytime" excludes the Halted state, contradicting FR-008's restriction.
- **Suggested resolution**: qualify FR-001 to "anytime in Normal state" or merge the Halted exception from FR-008 into FR-001.

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
